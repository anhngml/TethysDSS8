from tethys_sdk.base import TethysAppBase


class WaterQualityIndex(TethysAppBase):
    """
    Tethys app class for Water Quality Index.
    """

    name = 'Water Quality Index'
    description = ''
    package = 'water_quality_index'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'water-quality-index'
    color = '#524745'
    tags = ''
    enable_feedback = False
    feedback_emails = []