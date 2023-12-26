from tethys_sdk.base import TethysAppBase
from tethys_sdk.app_settings import CustomSetting, PersistentStoreDatabaseSetting,JSONCustomSetting, SpatialDatasetServiceSetting

class Threedidatacraft(TethysAppBase):
    """
    Tethys app class for Threedidatacraft.
    """

    name = 'Threedidatacraft'
    description = ''
    package = 'threedidatacraft'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'threedidatacraft'
    color = '#2f3640'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    THREDDS_SERVICE_NAME = 'thredds_service'

    # def spatial_dataset_service_settings(self):
    #     """
    #     Example spatial_dataset_service_settings method.
    #     """
    #     sds_settings = (
    #         SpatialDatasetServiceSetting(
    #             name=self.THREDDS_SERVICE_NAME,
    #             description='THREDDS service for app to use',
    #             engine=SpatialDatasetServiceSetting.THREDDS,
    #             required=True,
    #         ),
    #     )
    #     return sds_settings

    def custom_settings(self):
        custom_settings = (
            CustomSetting(
                name='points_sheet',
                type=CustomSetting.TYPE_STRING,
                description='Tên sheet chứa danh sách các điểm.',
                required=True,
                default="Format_1D_bond_Copy"
            ),
            CustomSetting(
                name='datetime_format',
                type=CustomSetting.TYPE_STRING,
                description='Định dạng thời gian của dữ liệu.',
                required=True,
                default="%m/%d/%Y %H:%M"
            ),
            JSONCustomSetting(
                name='boundary_type_map',
                description='Tên sheet tương ứng với boundary_type.',
                required=True,
                default={"1": {"sheet_name":"Waterlevel","time_column":1,"station_name_row":2,"first_data_row":4},
                         "2": {"sheet_name":"Velocity","time_column":1,"station_name_row":1,"first_data_row":3},
                         "3": {"sheet_name":"Discharge","time_column":1,"station_name_row":1,"first_data_row":3}}
            ),
            CustomSetting(
                name='thredds_data_root',
                type=CustomSetting.TYPE_STRING,
                description='Đường dẫn thư mục lưu dữ liệu của THREDDS.',
                required=True,
                default="E:/Tethys/thredds/public/mkdc"
            ),
        )

        return custom_settings