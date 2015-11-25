import subprocess
import pprint

translator = {  'file_size': '-f',
                'write_size': '-w',
                'n_writes': '-n',
                'pattern': '-p',
                'fsync': '-y',
                'sync': '-s',
                'file_path': '-l',
                'tag': '-t'
              }


def parse_player_runtime_out(lines):
    d = {}
    for line in lines:
        items = line.split()
        if len(items) == 2:
            d[items[0]] = items[1]

    return d


class MultiWriters(object):
    def __init__(self, player_path, parameters):
        """
        parameters is a list of dictionaries
        [
          { 'file_size':
            'write_size':
            'n_writes':
            'pattern':
            'fsync':
            'sync':
            'file_path':
            'tag':
          },
          ...
        ]
        """
        args = []
        for para in parameters:
            arg = [player_path, ]
            for k, v in para.items():
                arg.append(translator[k])
                arg.append(str(v))
            args.append(arg)

        # each row is a args for a player instance
        self.args_table = args

    def run(self):
        procs = []

        for args in self.args_table:
            print ' '.join(args)
            p = subprocess.Popen(args, stdout = subprocess.PIPE)
            procs.append(p)

        for p in procs:
            p.wait()

        results = []
        for p in procs:
            lines = p.communicate()[0].split('\n')
            d = parse_player_runtime_out(lines)
            d['pid'] = p.pid
            results.append(d)

        pprint.pprint( results )


def main():
    parameters = [
          { 'file_size': 40960,
            'write_size': 4096,
            'n_writes': 10,
            'pattern': 'random',
            'fsync': 1,
            'sync': 1,
            'file_path': '/tmp/frompython',
            'tag': 'mytag001'
          },
          { 'file_size': 40960,
            'write_size': 4096,
            'n_writes': 10,
            'pattern': 'random',
            'fsync': 0,
            'sync': 1,
            'file_path': '/tmp/frompython',
            'tag': 'mytag002'
           }
    ]

    mw = MultiWriters('./player-runtime', parameters)
    mw.run()


if __name__ == '__main__':
    main()

