from flask import request
from flask_restful import reqparse
from app.auth.utils import required_login
from app.cloudstack.cloudstack_base_resource import CloudstackResource, handle_errors
import app


class ProjectResource(CloudstackResource):

    @required_login
    @handle_errors
    def get(self, region):
        self._validate_params()
        account_name = self.args['account_name']
        domain_id = self.args['domain_id']

        parameters = {"domainid": domain_id,  "simple": "true", "listall": "true"}
        if self.args.get('is_admin') != 'true':
            parameters["account"] = account_name

        response = self.get_cloudstack(region).listProjects(parameters)

        if response.get('errortext') is not None:
            app.logger.error("Error while retrieving data from cloudstack: %s" % response['errortext'])
            return {"message": response['errortext']}, 400

        return self._to_json(response)

    def _validate_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('account_name', required=True, type=str, help='account_name must be informed')
        parser.add_argument('domain_id', required=True, type=str, help='domain_id must be informed')
        parser.add_argument('is_admin')
        self.args = parser.parse_args(req=request)

    def _to_json(self, response):
        if response is not None and response.get('count') is not None:
            return [
                {"name": self._get_project_name(project), "id": project['id'], "vm_count": project["vmtotal"],
                 "account": project["account"]} for project in response['project']
            ]
        else:
            return []

    def _get_project_name(self, project):
        if '' != project.get("displaytext") and project.get("displaytext") is not None:
            return project.get("displaytext")
        else:
            return project.get("name")
