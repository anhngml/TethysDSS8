from tethys_sdk.base import TethysAppBase
from tethys_sdk.app_settings import CustomSetting, PersistentStoreDatabaseSetting


class WaterLevel(TethysAppBase):
    """
    Tethys app class for Water Level.
    """

    name = 'Water Level'
    description = 'Water level prediction and viz'
    package = 'water_level'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'water-level'
    color = '#524745'
    tags = 'Hydrology'
    enable_feedback = False
    feedback_emails = []

    def custom_settings(self):
        """
        username = '__key__'
        password = 'PhqT72Cf.XIPKIPRazPtQ0qrEAQhZvjrV1Ey9AlDq'
        """
        custom_settings = (
            CustomSetting(
                name='datamart_username',
                type=CustomSetting.TYPE_STRING,
                description='Username for hydrology monitoring network.',
                required=True,
                default="__key__"
            ),
            CustomSetting(
                name='datamart_api_key',
                type=CustomSetting.TYPE_STRING,
                description='API key for hydrology monitoring network.',
                required=True,
                default="PhqT72Cf.XIPKIPRazPtQ0qrEAQhZvjrV1Ey9AlDq"
            ),
        )

        return custom_settings

    def persistent_store_settings(self):
        """
        Define Persistent Store Settings.
        """
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name='primary_db',
                description='primary database',
                initializer='water_level.model.init_primary_db',
                required=True
            ),
        )

        return ps_settings