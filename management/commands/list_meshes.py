from django.core.management.base import BaseCommand

from meshmgr.models import CountryMesh, AdhocMesh, MeshMember

from optparse import make_option


class Command(BaseCommand):
    args = '(none)'
    help = 'List all meshes'

    option_list = BaseCommand.option_list + (
        make_option(
            '--details',
            action='store_true',
            dest='details',
            default=None,
            help='Be more verbose'
        ),
    )

    def handle(self, *args, **options):
        for mesh in CountryMesh.objects.all():
            self.print_details(mesh, options)
        for mesh in AdhocMesh.objects.all():
            self.print_details(mesh, options)

    def print_details(self, mesh, options):
        print('%s (ID=%d, enabled=%s)' % (mesh, mesh.pk, mesh.enabled))
        if options['details']:
            self.print_member_details(mesh.pk)

    def print_member_details(self, mesh_id):
        for member in MeshMember.objects.filter(mesh=mesh_id):
            print('Probe #%s, msm_v4=%s, msm_v6=%s' % (member.prb_id, member.msm4_id, member.msm6_id))
