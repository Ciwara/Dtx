from django.core.management.commands.shell import Command as ShellCommand


class Command(ShellCommand):
    shells = ['ptpython', 'ipython', 'bpython']

    def ptpython(self):
        from prompt_toolkit.contrib.repl import embed
        embed(globals(), locals(), vi_mode=False, history_filename=None)
