def when_ready(server):
    from django.core.management import call_command
    call_command('validate')
