from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from meshmgr.models import Mesh, CountryMesh, AdhocMesh


class Command(BaseCommand):
    args = '(none)'
    help = 'Update probes or meshes'

    option_list = BaseCommand.option_list + (
        make_option(
            '-d',
            action='store_true',
            dest='show_dates',
            help='Echo starting/ending dates'
        ),
        make_option(
            '-p',
            action='store_true',
            dest='probes',
            help='Update probe list'
        ),
        make_option(
            '-m',
            action='store_true',
            dest='measurements',
            help='Update measurement meshes'
        )
    )

    def handle(self, *args, **options):

        if options['show_dates']:
            print('Starting at %s' % now())

        if not options['probes'] and not options['measurements']:
            print('Nothing to do -- you should specify -m or -p')

        if options['probes']:
            for mesh in CountryMesh.objects.filter(enabled=True):
                mesh.update_mesh_members()

        if options['measurements']:
            for mesh in CountryMesh.objects.filter(enabled=True):
                print('Checking & updating %s' % mesh)
                mesh.update_mesh_measurements()
            for mesh in AdhocMesh.objects.filter(enabled=True):
                print('Checking & updating %s' % mesh)
                mesh.update_mesh_measurements()

        if options['show_dates']:
            print('Finished at %s' % now())
