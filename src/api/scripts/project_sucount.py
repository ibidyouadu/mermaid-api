import csv
from django.test.client import Client
from django.urls import reverse
from ..utils import tokenutils
from ..models import BeltFishSUSQLModel, Project



# client = Client()
#
#
# def _call(client, token, url):
#     response = client.get(url, HTTP_AUTHORIZATION=f"Bearer {token}")
#     data = response.json()
#     return data["count"], data["results"], response


def run():
    with open("/var/projects/webapp/project_sucounts_temp.csv", "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["project_id", "sucount"])

        for project in Project.objects.order_by("id"):
            sucount = BeltFishSUSQLModel.objects.all().sql_table(project_id=project.id).count()
            csvwriter.writerow([project.id, sucount])

    # qry = BeltFishSUSQLModel.objects.all().sql_table(project_id="00673bdf-b838-4c2e-a305-86c99c378ec5")
    # print(qry.query, file=open("/var/projects/webapp/bfsuquery_1703.sql", "w"))
