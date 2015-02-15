
from django.utils.timezone import now
from django.db import models

from meshmgr.logic import get_probe_data_from_api, get_probe_data
from meshmgr.logic import make_measurement, check_probe_involvement, stop_measurement


class Mesh(models.Model):

    added     = models.DateTimeField(auto_now_add=True)
    enabled   = models.BooleanField(default=True)
    last_sync = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Mesh'

    def update_mesh_members(self):
        print('update_mesh_members() called on an abstract mesh')

    def check_and_involve_probes(self, probe_list):
        checked_probes = 0
        added_probes = 0
        up_probes = 0
        public_probes = 0
        status_changed_probes = 0
        for probe_id in probe_list:
            probe = get_probe_data(probe_id)
            checked_probes += 1
            probe_status = probe['status']
            probe_public = probe['is_public']
            if probe_status == 1:
                up_probes += 1
            if probe_public == 1:
                public_probes += 1

            try:
                probe_in_mesh = MeshMember.objects.filter(mesh=self.pk, prb_id=probe_id)[0]
                if probe_in_mesh.prb_last_status != probe_status or probe_in_mesh.prb_last_public != probe_public:
                    status_changed_probes += 1
            except IndexError:
                print('Adding probe %d to %s' % (probe_id, self))
                probe_in_mesh = MeshMember()
                probe_in_mesh.prb_id = probe_id
                probe_in_mesh.mesh = self
                added_probes += 1
            probe_in_mesh.prb_last_status = probe_status
            probe_in_mesh.prb_last_public = probe_public
            try:
                probe_in_mesh.prb_last_ipv4 = probe['address_v4']
            except KeyError:
                pass
            try:
                probe_in_mesh.prb_last_ipv6 = probe['address_v6']
            except KeyError:
                pass
            probe_in_mesh.save()

        print('Involvement check: %d probes checked, %d added. %d probes up, %d public, %d changed.'
              % (checked_probes, added_probes, up_probes, public_probes, status_changed_probes))

    def update_mesh_measurements(self):

        # IPv4
        probe_list = list(
            self.members.values('prb_id').
            filter(prb_last_public=True, prb_last_status=1, prb_last_ipv4__isnull=False).
            values_list('prb_id', flat=True)
        )
        for m in self.members.filter(prb_last_public=True, prb_last_status=1, prb_last_ipv4__isnull=False):

            # clone probe list and remove this probe
            probe_list_excl = probe_list[:]
            probe_list_excl.remove(m.prb_id)

            if m.msm4_id is None:
                msm_id = make_measurement(
                    m.prb_id,
                    4,
                    m.prb_last_ipv4,
                    probe_list_excl,
                    'Atlas MeshManager %s, target %s, IPv4' % (self, m)
                )
                m.msm4_id = msm_id
                m.msm4_added = now()
                m.save()
            else:
                check_probe_involvement(
                    m.msm4_id,
                    probe_list_excl
                )

        # IPv6
        probe_list = list(
            self.members.values('prb_id').
            filter(prb_last_public=True, prb_last_status=1, prb_last_ipv6__isnull=False).
            values_list('prb_id', flat=True)
        )
        for m in self.members.filter(prb_last_public=True, prb_last_status=1, prb_last_ipv6__isnull=False):

            # clone probe list and remove this probe
            probe_list_excl = probe_list[:]
            probe_list_excl.remove(m.prb_id)

            if m.msm6_id is None:
                msm_id = make_measurement(
                    m.prb_id,
                    6,
                    m.prb_last_ipv6,
                    probe_list_excl,
                    'Atlas MeshManager %s, target %s, IPv6' % (self, m)
                )
                m.msm6_id = msm_id
                m.msm6_added = now()
                m.save()
            else:
                check_probe_involvement(
                    m.msm6_id,
                    probe_list_excl
                )
        return

    def stop(self):
        print('Stopping mesh')
        self.enabled = False
        self.save()
        for member in self.members.values('msm4_id','msm6_id'):
            if member['msm4_id'] != None:
                stop_measurement( member['msm4_id'] )
                raw_input("Press Enter to continue...") 
            if member['msm6_id'] != None:
                stop_measurement( member['msm6_id'] )
                raw_input("Press Enter to continue...") 

class CountryMesh(Mesh):
    continent    = models.CharField(max_length=2)
    iso3166      = models.CharField(max_length=2, unique=True)
    country_name = models.CharField(max_length=64)

    def __unicode__(self):
        return u'Country mesh: %s' % self.iso3166

    def update_mesh_members(self):
        print('Updating probes for country mesh: %s' % self.iso3166)
        probe_list = get_probe_data_from_api([('country_code=%s' % self.iso3166)])
        self.check_and_involve_probes(probe_list)


class AdhocMesh(Mesh):
    descr = models.CharField(max_length=64)

    def __unicode__(self):
        return u'Ad-hoc mesh: %s' % self.descr

    def update_mesh_members(self):
        return



class MeshMember(models.Model):
    mesh            = models.ForeignKey('Mesh',related_name='members')
    prb_id          = models.IntegerField(null=False)
    prb_added       = models.DateTimeField(auto_now_add=True)
    prb_last_public = models.BooleanField(null=False, default=False)
    prb_last_status = models.IntegerField(null=False)
    prb_last_ipv4   = models.CharField(null=True, max_length=16)
    prb_last_ipv6   = models.CharField(null=True, max_length=64)
    prb_last_check  = models.DateTimeField(null=False, auto_now_add=True, auto_now=True)
    msm4_id         = models.IntegerField(null=True)
    msm4_added      = models.DateTimeField(null=True)
    msm6_id         = models.IntegerField(null=True)
    msm6_added      = models.DateTimeField(null=True)

    def __unicode__(self):
        return 'probe: %d' % self.prb_id
