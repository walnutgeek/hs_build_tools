import os
import sys

from sniffer.api import file_validator, runnable


@file_validator
def py_files(filename):
    return filename.endswith('.py') or filename.endswith(
        '.yaml') or filename.endswith('.rst')


run_envs = ['hb36', 'hb37']


mypy_modules = ['hs_build_tools',
                'hs_build_tools.pytest',
                'hs_build_tools.nose',
                'hs_build_tools.runenv',
                'hs_build_tools.release']


def os_system_in_env(e,cmd):
    return os.system(cmd if e == 'current' else f'. activate {e}; {cmd}')

def run_suite(env, case, nose):
    if nose:
        return os_system_in_env(env, f'python -m coverage run -p -m nose {case}')
    else:
        if case:
            case = '-m "not slow"'
        return os_system_in_env(env, f'python -m coverage run -p -m pytest {case}')

def run_tests(case, envs, html=False):

    env_states = [0 == run_suite(e, case, nose=False) for e in envs]
    print(dict(zip(envs, env_states)))
    modules = ' '.join( f'-m {m}' for m in mypy_modules )
    mypy = 0 == os_system_in_env(envs[0],
        f'python -m mypy {modules} --ignore-missing-imports'
    )
    cleanup_cmds = [
        'python -m coverage combine',
        'python -m coverage report -m',
    ]
    if html:
        cleanup_cmds.append('python -m coverage html')
    for c in cleanup_cmds:
        os_system_in_env(envs[0], c)
    os.unlink('.coverage')
    return all(env_states) and mypy

"""
Tests to add:


"""

@runnable
def execute_some_tests(*args):
    case = ''
    case += ' hs_build_tools.tests.nose_tests'
    return run_tests(case, run_envs, html=True)



if __name__ == '__main__':
    envs = run_envs
    cmd = 'test'
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if len(sys.argv) > 2 :
            envs = sys.argv[2:]
    if cmd == 'test':
        if not(run_tests('', envs, html=True)):
            raise SystemExit(-1)
    elif cmd == 'cleanup_envs':
        for env in envs:
            os.system(f'conda env remove -y -n {env}')
    elif cmd == 'setup_envs':
        for env in envs:
            ver = ".".join(env[-2:])
            os.system(f'conda create -y -n {env} python={ver}')
            os.system(f'. activate {env}; pip install -e .[dev]')

