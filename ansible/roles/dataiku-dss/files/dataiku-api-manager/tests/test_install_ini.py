from src.dataiku_controller import DataikuController
from src.dss_install_ini import InstallIni


def test_install_ini():
    controller = DataikuController('tests/dummy_commands', None)

    data = {
        'new_category': {
            'my_key': 'my_value'
        },
        'javaopts': {
            'backend.xmx': '2g'
        }
    }

    install = InstallIni('tests/install.ini', data, controller)

    data = install.set_configuration()

    assert data.sections() == ['general', 'server', 'git', 'javaopts', 'new_category']
    assert data.items('general') == [('nodetype', 'design'), ('installid', '1234')]
    assert data.items('server') == [('port', '11200')]
    assert data.items('git') == [('mode', 'project')]
    assert data.items('javaopts') == [('backend.xmx', '2g')]
    assert data.items('new_category') == [('my_key', 'my_value')]

