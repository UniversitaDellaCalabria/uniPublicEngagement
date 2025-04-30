from django.urls import path

from . api.views import (generic as api_generic,
                         user as api_user,
                         operator as api_evaluation_operator,
                         patronage as api_patronage_operator,
                         manager as api_manager,
                         involved_personnel as api_involved_personnel,
                         involved_structures as api_involved_structures)

from . views import (generic,
                     involved_personnel,
                     involved_structures,
                     manager,
                     operator,
                     patronage,
                     user)


app_name = 'pe_management'


# app prefix
prefix = 'pe-management'

api_prefix = "api"
user_prefix = 'user'
involved_personnel_prefix = 'involved-personnel'
involved_structures_prefix = 'involved-structures'
operator_prefix = 'operator'
validator_prefix = 'evaluation'
patronage_prefix = 'patronage'
manager_prefix = 'manager'

urlpatterns = [
    path(f'{prefix}/', generic.dashboard, name='dashboard'),
    path(f'{prefix}/events/<int:event_id>/poster/download/', generic.download_event_poster, name='download_event_poster'),

    # user
    path(f'{prefix}/{user_prefix}/events/', user.events, name='user_events'),
    path(f'{prefix}/{user_prefix}/events/new/',
         user.new_event_choose_referent, name='user_new_event_choose_referent'),
    path(f'{prefix}/{user_prefix}/events/new/basic-info/',
         user.new_event_basic_info, name='user_new_event_basic_info'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/',
         user.event, name='user_event'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/basic-info/',
         user.event_basic_info, name='user_event_basic_info'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/data/',
         user.event_data, name='user_event_data'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/report/',
         user.event_report, name='user_event_report'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/people/',
         user.event_people, name='user_event_people'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/people/delete/<int:person_id>/',
         user.event_people_delete, name='user_event_people_delete'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/structures/',
         user.event_structures, name='user_event_structures'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/structures/delete/<int:structure_id>/',
         user.event_structures_delete, name='user_event_structures_delete'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/request-evaluation/',
         user.event_request_evaluation, name='user_event_request_evaluation'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/request-evaluation-cancel/',
         user.event_request_evaluation_cancel, name='user_event_request_evaluation_cancel'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/clone/',
         user.event_clone, name='user_event_clone'),
    path(f'{prefix}/{user_prefix}/events/<int:event_id>/delete/',
         user.event_delete, name='user_event_delete'),

    # evaluation operator
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/',
         operator.dashboard, name='operator_dashboard'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/',
         operator.events, name='operator_events'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/',
         operator.event, name='operator_event'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/take/',
         operator.take_event, name='operator_take_event'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/basic-info/',
         operator.event_basic_info, name='operator_event_basic_info'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/data/',
         operator.event_data, name='operator_event_data'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/people/',
         operator.event_people, name='operator_event_people'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/people/delete/<int:person_id>/',
         operator.event_people_delete, name='operator_event_people_delete'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/structures/',
         operator.event_structures, name='operator_event_structures'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/structures/delete/<int:structure_id>/',
         operator.event_structures_delete, name='operator_event_structures_delete'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/evaluate/',
         operator.event_evaluation, name='operator_event_evaluation'),
    path(f'{prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/<int:event_id>/reopen-evaluation/',
         operator.event_reopen_evaluation, name='operator_event_reopen_evaluation'),

    # patronage operator
    path(f'{prefix}/{operator_prefix}/{patronage_prefix}/',
         patronage.dashboard, name='patronage_operator_dashboard'),
    path(f'{prefix}/{operator_prefix}/{patronage_prefix}/<str:structure_slug>/events/',
         patronage.events, name='patronage_operator_events'),
    path(f'{prefix}/{operator_prefix}/{patronage_prefix}/<str:structure_slug>/events/<int:event_id>/',
         patronage.event, name='patronage_operator_event'),
    path(f'{prefix}/{operator_prefix}/{patronage_prefix}/<str:structure_slug>/events/<int:event_id>/take/',
         patronage.take_event, name='patronage_operator_take_event'),
    path(f'{prefix}/{operator_prefix}/{patronage_prefix}/<str:structure_slug>/events/<int:event_id>/evaluate/',
         patronage.event_evaluation, name='patronage_operator_event_evaluation'),
    path(f'{prefix}/{operator_prefix}/{patronage_prefix}/<str:structure_slug>/events/<int:event_id>/reopen-evaluation/',
         patronage.event_reopen_evaluation, name='patronage_operator_event_reopen_evaluation'),

    # involved structures
    path(f'{prefix}/{operator_prefix}/{involved_structures_prefix}/',
         involved_structures.dashboard, name='involved_structures_dashboard'),
    path(f'{prefix}/{operator_prefix}/{involved_structures_prefix}/<str:structure_slug>/events/',
        involved_structures.events, name='involved_structures_events'),
    path(f'{prefix}/{operator_prefix}/{involved_structures_prefix}/<str:structure_slug>/events/<int:event_id>/',
        involved_structures.event, name='involved_structures_event'),

    # manager
    path(f'{prefix}/{manager_prefix}/',
         manager.dashboard, name='manager_dashboard'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/',
         manager.events, name='manager_events'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/new/',
         manager.new_event_choose_referent, name='manager_new_event_choose_referent'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/new/basic-info/',
         manager.new_event_basic_info, name='manager_new_event_basic_info'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/',
         manager.event, name='manager_event'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/basic-info/',
         manager.event_basic_info, name='manager_event_basic_info'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/data/',
         manager.event_data, name='manager_event_data'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/people/',
         manager.event_people, name='manager_event_people'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/people/delete/<int:person_id>/',
         manager.event_people_delete, name='manager_event_people_delete'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/structures/',
         manager.event_structures, name='manager_event_structures'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/structures/delete/<int:structure_id>/',
         manager.event_structures_delete, name='manager_event_structures_delete'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/report/',
         manager.event_report, name='manager_event_report'),
    path(f'{prefix}/{manager_prefix}/<str:structure_slug>/events/<int:event_id>/change-status/',
         manager.event_enable_disable, name='manager_event_enable_disable'),

    # involved personnel
    path(f'{prefix}/{involved_personnel_prefix}/events/', involved_personnel.events, name='involved_personnel_events'),
    path(f'{prefix}/{involved_personnel_prefix}/events/<int:event_id>/',
         involved_personnel.event, name='involved_personnel_event'),

    # API
    path(f'{prefix}/{api_prefix}/structures/', api_generic.OrganizationalStructureList.as_view(), name='api_structures'),
    path(f'{prefix}/{api_prefix}/events/',
         api_generic.PublicEngagementApprovedEventList.as_view(), name='api_generic_approved_events'),
    path(f'{prefix}/{api_prefix}/events/<int:pk>/',
         api_generic.PublicEngagementApprovedEventDetail.as_view(), name='api_generic_approved_event'),
    path(f'{prefix}/{api_prefix}/{user_prefix}/events/',
         api_user.PublicEngagementEventList.as_view(), name='api_user_events'),
    path(f'{prefix}/{api_prefix}/{operator_prefix}/{validator_prefix}/<str:structure_slug>/events/',
         api_evaluation_operator.PublicEngagementEventList.as_view(), name='api_evaluation_operator_events'),
    path(f'{prefix}/{api_prefix}/{operator_prefix}/{patronage_prefix}/<str:structure_slug>/events/',
         api_patronage_operator.PublicEngagementEventList.as_view(), name='api_patronage_operator_events'),
    path(f'{prefix}/{api_prefix}/{manager_prefix}/<str:structure_slug>/events/',
         api_manager.PublicEngagementEventList.as_view(), name='api_manager_events'),
    path(f'{prefix}/{api_prefix}/{involved_personnel_prefix}/events/',
         api_involved_personnel.PublicEngagementEventList.as_view(), name='api_involved_personnel_events'),
    path(f'{prefix}/{api_prefix}/{operator_prefix}/{involved_structures_prefix}/<str:structure_slug>/events/',
         api_involved_structures.PublicEngagementEventList.as_view(), name='api_involved_structures_events'),
]
