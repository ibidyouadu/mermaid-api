from api.models import BeltFishObsSQLModel, SampleEvent
from api.utils.timer import Timer

# from scalene import profile


# pk = "8c213ce8-7973-47a5-9359-3a0ef12ed201"
pk = "75ef7a5a-c770-4ca6-b9f8-830cab74e425"


# @mprofile
def test1():
    return BeltFishObsSQLModel.objects.all().sql_table(
        project_id=pk
    )

# @profile
def test2():
    sample_events = list(SampleEvent.objects.filter(site__project_id=pk))
    i = 0
    chunks = 10
    for i in range(0, len(sample_events), chunks):
        yield BeltFishObsSQLModel.objects.all().sql_table(
            project_id=pk, sample_event_id=",".join(f"'{se.id}'::uuid" for se in sample_events[i:i+chunks])
        )

def run():
    
    with Timer("Test1"):
        data1 = list(test1())
        print(len(data1))
    
    # with Timer("Test2"):
    #     data2 = []
    #     cnt = 0
    #     for t in test2():
    #         cnt = len(list(t))
    #     print(cnt)