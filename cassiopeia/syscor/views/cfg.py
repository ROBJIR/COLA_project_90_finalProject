"""
web_page_attributes_template = {
        "application_code": "",
        "application_name": "",
        "application_module_start": "",
        "module_code": "",
        "module_name": "",
        "module_file_template": "",
        "application_file_menu": "",
"""

WEB_APPLICATIONS = {
    'cassiopeia':{'application_name':'Cassiopeia Project',      'application_module_start': 'cassiopeia',  'application_file_menu':'syscor-menu-dropdown.html'},
    'sysadm'    :{'application_name':'System Administration',   'application_module_start': 'sysadm',      'application_file_menu':'sysadm-menu-dropdown.html'},
    'syslog'    :{'application_name':'System Logging',          'application_module_start': 'syslog',      'application_file_menu':'syslog-menu-dropdown.html'},
    'whohas'    :{'application_name':'Who Has My Stuff?',       'application_module_start': 'whohas',      'application_file_menu':'whohas-menu-dropdown.html'},
    'paidyet'   :{'application_name':'Paid yet?',               'application_module_start': 'paidyet',     'application_file_menu':'paidyet-menu-dropdown.html'},
}

WEB_APPLICATION_MODULES = {
# ===== syscor =======================================================================================
    '404':{'application_code': 'cassiopeia',        'module_name':          'Page not found!',
                                                    'module_file_template': '404_page_not_found.html'},
    '403': {'application_code': 'cassiopeia',       'module_name':          'Access Denied!',
                                                    'module_file_template': '403_access_denied.html'},
# ===== syscor =======================================================================================
    'cassiopeia':{'application_code': 'cassiopeia', 'module_name':          'Cassiopeia Project',
                                                    'module_file_template': 'syscor-main.html'},
    'userprofile': {'application_code': 'cassiopeia', 'module_name':        'User Profile',
                                                    'module_file_template': 'auth/auth-profile.html'},
    'userlogin': {'application_code': 'cassiopeia', 'module_name': 'Login',
                                                    'module_file_template': 'auth/auth-login.html'},
# ===== sysadm =======================================================================================
    'sysadm'    :{'application_code': 'sysadm',     'module_name':          'System Administration',
                                                    'module_file_template': 'sysadm.html'},
    'sessionsinfo': {'application_code': 'sysadm',  'module_name':          'Sessions Info',
                                                    'module_file_template': 'sysadm-sesscookielist.html'},
    'cookieinfo': {'application_code': 'sysadm',    'module_name':          'Sessions Info',
                                                    'module_file_template': 'sysadm-sesscookielist.html'},
    'sysadm-userlist': {'application_code': 'sysadm', 'module_name':         'Authority module: Users',
                                                    'module_file_template': 'sysadm-userlist.html'},
    'sysadm-grouplist': {'application_code': 'sysadm', 'module_name':       'Authority module: Grous',
                                                    'module_file_template': 'sysadm-grouplist.html'},
    'sysadm-permissionlist': {'application_code': 'sysadm', 'module_name':  'Admin module: Permitions',
                                                    'module_file_template': 'sysadm-permissionlist.html'},
# ===== syslog =======================================================================================
    'syslog'    :{'application_code': 'syslog',     'module_name':          'Cookie Info',
                                                    'module_file_template': 'syslog.html', },
    'webloglist': {'application_code': 'syslog',    'module_name':          'WebLog',
                                                    'module_file_template': 'webloglist.html', },
    'sysloglist': {'application_code': 'syslog',    'module_name':          'SysLog',
                                                    'module_file_template': 'sysloglist.html', },
# ===== whohas =======================================================================================
    'whohas'    :{'application_code': 'whohas',     'module_name':          'Who Has My Stuff?',
                                                    'module_file_template': 'whohas.html',},
# ===== paidyet =======================================================================================
    'paidyet'   :{'application_code': 'paidyet',    'module_name':          'Paid yet?',
                                                    'module_file_template': 'paidyet.html', },
}
