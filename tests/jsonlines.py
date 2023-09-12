import jsonlines
import json

data1=[
    {
        "name": "andryas"
    },
    {
        "name": "jao"
    }
]

with jsonlines.open('test.jsonl', mode='w') as writer:
    writer.write(data1)


data2=[
    {
        "name": "pedrao"
    },
    {
        "name": "kervao"
    }
]

with jsonlines.open('test.jsonl', mode='a') as writer:
    writer.write(data2)

data=[]
with jsonlines.open('test.jsonl') as reader:
    for obj in reader:
        data.append(obj)
data