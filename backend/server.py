#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @filename: server
# @date: 2023/9/16

import json
import os
import re
import time
import traceback

import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


sagemaker_runtime = boto3.client("sagemaker-runtime",
                                 region_name="us-west-2",
                                 aws_access_key_id="AKIAQSLD5VQOWP3HFUHU",
                                 aws_secret_access_key="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"
                                 )

endpoint_name = "cpm-bee-230916102019ZRIZ"

robot_helper_text = """
        作为一个具有广泛世界各地地点知识的智能行程规划师，您的任务是根据用户的消息确定他们的旅行目的地以及任何特定的兴趣或偏好。创建一个迎合用户需求的行程，确保具体命名所有活动、餐馆和景点。在创建行程时，还要考虑到时间限制和交通选择等因素。此外，行程中列出的所有景点和餐馆必须存在并具体命名。在后续修订中，行程可以进行修改，同时要考虑行程的实际可行性。每天都要选择新的地点。重要的是要确保每天的活动数量适当，如果用户没有另外指定，那么默认的行程长度是五天。行程长度应保持不变，除非用户的消息有变化。
        以下是前往香港的五天行程示例：\n\n第一天:\n* 抵达[香港国际机场（HKG）|香港]。\n* 乘坐出租车或机场巴士前往[香港岛|香港]的酒店。\n* 探索[中环区|香港岛]，包括[太平山|香港]、[文武庙|香港]和[荷里活道|香港]。\n* 在[中环|香港岛]的餐厅用晚餐，比如[兰芳园|香港]。\n\n第二天:\n* 乘坐渡轮前往[大屿山|香港]。\n* 参观[天坛大佛|香港]，一座巨大的铜像，以及[宝莲寺|香港]。\n* 探索[昂坪村|香港]及其景点。\n* 傍晚返回[香港岛|香港]。\n\n第三天:\n* 探索[九龙|香港]，包括[尖沙咀|香港]、[海港城|香港]和[星光大道|香港]。\n* 参观[香港历史博物馆|香港]，了解这座城市丰富的文化遗产。\n* 在[旺角|香港]繁华地区购物和品尝街头美食。\n* 在[旺角|香港]的当地餐馆用晚餐，比如[麦奀面家|香港]。\n\n第四天:\n* 进行一日游，前往[南丫岛|香港]。\n* 探索风景秀丽的地方，远足径和[南丫风力发电站|香港]。\n* 在海边餐厅享用海鲜，比如[彩虹海鲜餐厅|香港]。\n* 傍晚返回[香港岛|香港]。\n\n第五天:\n* 参观[香港迪士尼乐园|香港]，度过一个充满魔法的一天。\n* 探索各种主题区域，享受刺激的游乐设施。\n* 在园内用午餐和晚餐。\n* 返回你的家乡。\n\n这个行程可以根据你的兴趣和预算进行定制。如果你对艺术感兴趣，考虑参观[香港艺术博物馆|香港]。如果你热爱大自然，探索[西贡|香港]的美丽海滩和地质公园。如果你是美食家，那就深入[庙街夜市|香港]，寻找更多的美食冒险。\n\n无论你的兴趣或预算如何，我希望你在香港度过一个美妙的时光！"
"""


def invoke_inference_endpoint(endpoint_name, arr_input, max_new_tokens=1024):
    input = {
        "inputs": arr_input,
        "parameters": {"max_new_tokens": max_new_tokens, "repetition_penalty": 1.1, "temperature": 0.5}
    }
    start_time = time.time()  # Start the timer
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        Body=bytes(json.dumps(input), 'utf-8'),
        ContentType='application/json',
        Accept='application/json'
    )
    end_time = time.time()  # End the timer
    elapsed_time = round(end_time - start_time, 2)
    print(f"Endpoint invocation took {elapsed_time} seconds")
    response_json = json.load(response['Body'])
    return response_json


@app.route('/api/query', methods=['POST'])
def receive_post_request():
    if request.method == 'POST':
        print(request.get_json())
        data = request.get_json()  # 获取POST请求的JSON数据
        query = data.get('query')
        if not query:
            return jsonify({'message': ''})
        try:
            req_data = {
                "input": robot_helper_text,
                "prompt": query,
                "<ans>": ""
            }
            answer = invoke_inference_endpoint(
                endpoint_name,
                [req_data]
            )
            result = answer['data'][0]['<ans>']
            # result = robot_helper_text
            tags = []
            for item in re.findall(r'\[(.*?)\]', result):
                item = item.strip()
                groups = item.split('|')
                if len(groups) < 2:
                    continue
                city = groups[1]
                address = groups[0]
                tag = city + address
                tags.append(tag)
            return jsonify({'message': result.strip(), 'tags': tags})
        except:
            traceback.print_exc()


if __name__ == '__main__':
    # input1 = {
    #     "input": """
    #     作为一个具有广泛世界各地地点知识的智能行程规划师，您的任务是根据用户的消息确定他们的旅行目的地以及任何特定的兴趣或偏好。创建一个迎合用户需求的行程，确保具体命名所有活动、餐馆和景点。在创建行程时，还要考虑到时间限制和交通选择等因素。此外，行程中列出的所有景点和餐馆必须存在并具体命名。在后续修订中，行程可以进行修改，同时要考虑行程的实际可行性。每天都要选择新的地点。重要的是要确保每天的活动数量适当，如果用户没有另外指定，那么默认的行程长度是五天。行程长度应保持不变，除非用户的消息有变化。
    #     以下是前往香港的五天行程示例：\n\n第一天:\n* 抵达[香港国际机场（HKG）|香港]。\n* 乘坐出租车或机场巴士前往[香港岛|香港]的酒店。\n* 探索[中环区|香港岛]，包括[太平山|香港]、[文武庙|香港]和[荷里活道|香港]。\n* 在[中环|香港岛]的餐厅用晚餐，比如[兰芳园|香港]。\n\n第二天:\n* 乘坐渡轮前往[大屿山|香港]。\n* 参观[天坛大佛|香港]，一座巨大的铜像，以及[宝莲寺|香港]。\n* 探索[昂坪村|香港]及其景点。\n* 傍晚返回[香港岛|香港]。\n\n第三天:\n* 探索[九龙|香港]，包括[尖沙咀|香港]、[海港城|香港]和[星光大道|香港]。\n* 参观[香港历史博物馆|香港]，了解这座城市丰富的文化遗产。\n* 在[旺角|香港]繁华地区购物和品尝街头美食。\n* 在[旺角|香港]的当地餐馆用晚餐，比如[麦奀面家|香港]。\n\n第四天:\n* 进行一日游，前往[南丫岛|香港]。\n* 探索风景秀丽的地方，远足径和[南丫风力发电站|香港]。\n* 在海边餐厅享用海鲜，比如[彩虹海鲜餐厅|香港]。\n* 傍晚返回[香港岛|香港]。\n\n第五天:\n* 参观[香港迪士尼乐园|香港]，度过一个充满魔法的一天。\n* 探索各种主题区域，享受刺激的游乐设施。\n* 在园内用午餐和晚餐。\n* 返回你的家乡。\n\n这个行程可以根据你的兴趣和预算进行定制。如果你对艺术感兴趣，考虑参观[香港艺术博物馆|香港]。如果你热爱大自然，探索[西贡|香港]的美丽海滩和地质公园。如果你是美食家，那就深入[庙街夜市|香港]，寻找更多的美食冒险。\n\n无论你的兴趣或预算如何，我希望你在香港度过一个美妙的时光！"
    #     """,
    #     "prompt": "我想去天津。",
    #     "<ans>": ""
    # }
    # # change to your endpoint
    # endpoint_name = "cpm-bee-230915042855LLMF"
    # r = invoke_inference_endpoint(
    #     endpoint_name,
    #     [input1]
    # )
    # print(r['data'][0]['<ans>'])
    app.run(debug=True)
