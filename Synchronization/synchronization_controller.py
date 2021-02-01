
from flask import Flask, request, Response
from injector import inject
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from flask_babel import gettext, _
from wtforms import StringField, Form
from wtforms.validators import DataRequired, ValidationError
from auth import admin_only
from Synchronization.synchronization_dto import SynchronizationDTO
from Synchronization.synchronization_service import SynchronizationService
from Synchronization.schedule_service import ScheduleService

from database_definition import Synchronization, SynchAction, SynchLog
from base_render import render_template

class ScheduleForm(Form):
    schedule = StringField(_('schedule'))

@inject
@admin_only
def synchronize(service: SynchronizationService):
    service.synchronize()
    return Response('', status=200)

@inject
@admin_only
def stop(service: ScheduleService):
    service.stop_job()
    return Response('', status=200)

@inject
@admin_only
def get_synchronization(service: SynchronizationService):
    synchId= int(request.args.get('synchId') or -1)
    synchronization, actions = service.get_synchronization(synchId)
    if synchronization is None:
        return Response('', status = 405)

    return render_template('synchronization.html', date = synchronization.date, actions = actions, id = synchId, modified = synchronization.get_number_of_modifications())

def validate(schedule, message):
    if schedule is None:
        raise ValidationError(message)

@admin_only
@inject
def synchronizations(service : ScheduleService):
    page = int(request.args.get('page') or 1)
    form = ScheduleForm(request.form)
    message = _("You have entered invalid cron")
    schedule = service.get_schedule(form.schedule.data)

    if form.validate(extra_validators= { 'schedule': [lambda form, field: validate(schedule, message)]}):
        service.start_job(schedule)
        return Response('', 200)

    entites = Synchronization.query.paginate(page, 20, False)
    dtos = [SynchronizationDTO(s) for s in entites.items]
    return render_template('synchronization_list.html', dtos = dtos, form = form, hasNext= entites.has_next, hasPrev = entites.has_prev, pageNumber = page)
