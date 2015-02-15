from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from meshmgr.models import Mesh, AdhocMesh


class Command(BaseCommand):
    args = '(none)'
    help = 'Manage ad-hoc meshes.'

    option_list = BaseCommand.option_list + (
        make_option(
            '--create',
            action='store',
            dest='create',
            default=None,
            help='Name of the ad-hoc mesh to create'
        ),
        make_option(
            '--stop',
            action='store_true',
            dest='stop',
            default=None,
            help='Stops the ad-hoc mesh from measuring'
        ),
        make_option(
            '--id',
            action='store',
            dest='id',
            default=None,
            help='ID of the mesh to add probes too, needed when adding probes to an existing ad-hoc mesh'
        ),
        make_option(
            '--add',
            action='append',
            type='int',
            dest='add',
            default=[],
            help='Probe IDs to add'
        ),
        make_option(
            '--remove',
            action='store',
            type='int',
            dest='remove',
            default=None,
            help='Does not work (would remove probe)'
        ),
    )

    def handle(self, *args, **options):

        if not options['create'] and not options['add'] and not options['stop']:
            raise CommandError('You must specify create, add or stop')

        mesh = None
        if options['create']:
            print('Creating ad-hoc mesh %s' % options['create'])
            if not options['add']:
                print('Note: you need to define members with --add-probe')
            mesh = AdhocMesh()
            mesh.descr = options['create']
            mesh.save()

        if options['add']:
            if not mesh:
                if not options['id']:
                    print('Please specify ad-hoc mesh ID')
                    return
                else:
                    mesh = Mesh.objects.get(pk=options['id'])
            else:
                mesh = Mesh.objects.get(pk=mesh.pk)
            mesh.check_and_involve_probes(options['add'])

        if options['stop']:
            if not options['id']:
                print('Please specify ad-hoc mesh ID')
                return
            else:
                mesh = Mesh.objects.get(pk=options['id'])
            mesh.stop()
