{
    'name': 'Project Attachments',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Smartbutton to view project and task attachments',
    'description': """
        Adds a smartbutton in project form view to view all attachments
        related to the project and its tasks.
    """,
    'author': 'Oscar Soto, SDi SL',
    'website': 'https://www.sdi.es',
    'depends': ['project', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}