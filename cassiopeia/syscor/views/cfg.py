"""
web_page_attributes_template = {
        "application_code": "-",
        "application_name": "-",
        "module_code": "-",
        "module_name": "-",
        "module_file_template": "-",
        "module_file_menu": "-",}
"""

WEB_APPLICATIONS = {
    'cassiopeia':{'application_name':'Cassiopeia Project',      'application_file_menu':'syscor-menu-line.html'},
    'sysadm'    :{'application_name':'System Administration',   'application_file_menu':'sysadm-menu-line.html'},
    'syslog'    :{'application_name':'System Logging',          'application_file_menu':'syslog-menu-line.html'},
    'whohas'    :{'application_name':'Who Has My Stuff?',       'application_file_menu':'whohas-menu-line.html'},
    'paidyet'   :{'application_name':'Paid yet?',               'application_file_menu':'paidyet-menu-line.html'},
}

WEB_APPLICATION_MODULES = {
# ===== syscor =======================================================================================
    'cassiopeia':{'application_code': 'cassiopeia', 'module_name':          'Cassiopeia Project',
                                                    'module_file_template': 'syscor-main.html'},
    'userprofile': {'application_code': 'cassiopeia', 'module_name': 'User Profile',
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
    'sysadm-userlist': {'application_code': 'sysadm', 'module_name':         'Admin module: Users',
                                                    'module_file_template': 'sysadm-userlist.html'},
# ===== syslog =======================================================================================
    'syslog'    :{'application_code': 'syslog',     'module_name':          'Cookie Info',
                                                    'module_file_template': 'syslog.html', },
# ===== whohas =======================================================================================
    'whohas'    :{'application_code': 'whohas',     'module_name':          'Who Has My Stuff?',
                                                    'module_file_template': 'whohas.html',},
# ===== paidyet =======================================================================================
    'paidyet'   :{'application_code': 'paidyet',    'module_name':          'Paid yet?',
                                                    'module_file_template': 'paidyet.html', },
}