from tethys_sdk.base import TethysAppBase


class Dss8(TethysAppBase):
    """
    Tethys app class for DSS 8.
    """

    name = 'DSS 8'
    description = 'DSS 8'
    package = 'dss_8'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'dss-8'
    color = '#f39c12'
    tags = ''
    enable_feedback = False
    feedback_emails = []