import argparse
from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_restful import reqparse
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import handle_errors
from app.auditing.models import Event, EventSchema


class AuditingEventResource(Resource):

    @required_login
    @handle_errors
    def get(self, region):
        args = self.parse_args()
        parameters = dict(args, **{'region' : region})
        result = Event.find_all_by(parameters, args.page, args.page_size)
        return { 'count': result.total, 'events': EventSchema(many=True).dump(result.items).data }

    def parse_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', required=False, type=int)
        parser.add_argument('page_size', required=False, type=int)
        parser.add_argument('start_date', required=False, type=self.valid_date)
        parser.add_argument('end_date', required=False, type=self.valid_date)
        return parser.parse_args(req=request)

    def valid_date(self, s):
        try:
            return datetime.strptime(s, '%d/%m/%Y %H:%M:%S')
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)