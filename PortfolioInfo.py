# -*- coding: utf-8 -*-
#! python3

from FetchPortfolio import request, GetHeader
import re, json

# For Oyami only, Do not mod it!

''' Ori data (ZH888882)
SNB.cubeType = 'ZH';

SNB.cubeInfo = {"id":888784,"name":"斗转星移","symbol":"ZH888882","description":"","active_flag":true,"star"
:0,"market":"hk","owner_id":6333308667,"created_at":1465646536545,"updated_at":1492565495499,"last_rb_id"
:26495910,"daily_gain":-0.3,"monthly_gain":1.11,"total_gain":66.48,"net_value":1.6648,"rank_percent"
:98.89,"annualized_gain_rate":66.48,"bb_rate":17.62,"following":false,"follower_count":1,"view_rebalancing"
:{"id":26495910,"status":"success","cube_id":888784,"prev_bebalancing_id":26370588,"category":"sys_rebalancing"
,"exe_strategy":"market_all","created_at":1492565495499,"updated_at":1492565495499,"cash_value":2.2e-7
,"cash":0,"error_code":null,"error_message":"你上一笔调仓已成交。","error_status":null,"holdings":[{"stock_id"
:1005109,"weight":47.91,"segment_name":"纺织、服饰及个人护理","segment_id":4739441,"stock_name":"天虹纺织","stock_symbol"
:"02678","segment_color":"#e05173","proactive":false,"volume":0.08138643,"textname":"undefined(02678
)","url":"/S/02678"},{"stock_id":1004981,"weight":27.48,"segment_name":"地产","segment_id":4878950,"stock_name"
:"碧桂园","stock_symbol":"02007","segment_color":"#d9633b","proactive":false,"volume":0.06027115,"textname"
:"undefined(02007)","url":"/S/02007"},{"stock_id":1004708,"weight":24.61,"segment_name":"家庭电器及用品","segment_id"
:4739440,"stock_name":"海尔电器","stock_symbol":"01169","segment_color":"#82b952","proactive":false,"volume"
:0.02226274,"textname":"undefined(01169)","url":"/S/01169"}],"rebalancing_histories":[],"comment":null
,"diff":0,"new_buy_count":0},"last_rebalancing":{"id":26495910,"status":"success","cube_id":888784,"prev_bebalancing_id"
:26370588,"category":"sys_rebalancing","exe_strategy":"market_all","created_at":1492565495499,"updated_at"
:1492565495499,"cash_value":2.2e-7,"cash":0,"error_code":null,"error_message":"你上一笔调仓已成交。","error_status"
:null,"holdings":[{"stock_id":1005109,"weight":47.91,"segment_name":"纺织、服饰及个人护理","segment_id":4739441
,"stock_name":"天虹纺织","stock_symbol":"02678","segment_color":"#e05173","proactive":false,"volume":0.08138643
},{"stock_id":1004981,"weight":27.48,"segment_name":"地产","segment_id":4878950,"stock_name":"碧桂园","stock_symbol"
:"02007","segment_color":"#d9633b","proactive":false,"volume":0.06027115},{"stock_id":1004708,"weight"
:24.61,"segment_name":"家庭电器及用品","segment_id":4739440,"stock_name":"海尔电器","stock_symbol":"01169","segment_color"
:"#82b952","proactive":false,"volume":0.02226274}],"rebalancing_histories":[],"comment":null,"diff":0
,"new_buy_count":0},"last_success_rebalancing":{"id":26495910,"status":"success","cube_id":888784,"prev_bebalancing_id"
:26370588,"category":"sys_rebalancing","exe_strategy":"market_all","created_at":1492565495499,"updated_at"
:1492565495499,"cash_value":2.2e-7,"cash":0,"error_code":null,"error_message":"你上一笔调仓已成交。","error_status"
:null,"holdings":[{"stock_id":1005109,"weight":47.91,"segment_name":"纺织、服饰及个人护理","segment_id":4739441
,"stock_name":"天虹纺织","stock_symbol":"02678","segment_color":"#e05173","proactive":false,"volume":0.08138643
},{"stock_id":1004981,"weight":27.48,"segment_name":"地产","segment_id":4878950,"stock_name":"碧桂园","stock_symbol"
:"02007","segment_color":"#d9633b","proactive":false,"volume":0.06027115},{"stock_id":1004708,"weight"
:24.61,"segment_name":"家庭电器及用品","segment_id":4739440,"stock_name":"海尔电器","stock_symbol":"01169","segment_color"
:"#82b952","proactive":false,"volume":0.02226274}],"rebalancing_histories":[],"comment":null,"diff":0
,"new_buy_count":0},"style":{"name":"小浪花","color0":"#4486ed","color1":"#4486ed","degree":30},"tag":["
纺织"],"recommend_reason":null,"sale_flag":false,"sell_flag":false,"commission":null,"initial_capital"
:null,"listed_flag":false,"contractor_id":null,"contractor_name":null,"last_user_rb_gid":26370588,"owner"
:{"subscribeable":false,"common_count":0,"remark":null,"recommend_reason":null,"recommend":null,"followers_count"
:1,"friends_count":56,"st_color":"1","follow_me":false,"verified":false,"intro":null,"stock_status_count"
:null,"screen_name":"暮远云","step":"three","gender":"n","province":"广东","city":"广州","blog_description"
:null,"verified_type":0,"verified_description":null,"last_status_id":79141368,"status_count":28,"donate_count"
:0,"allow_all_stock":false,"stocks_count":null,"blocking":false,"domain":null,"name":null,"location"
:null,"id":6333308667,"type":"1","description":"","status":1,"following":false,"profile":"/6333308667"
,"url":null,"profile_image_url":"community/20148/1410968142277-1410968147713.jpg,community/20148/1410968142277-1410968147713
.jpg!180x180.png,community/20148/1410968142277-1410968147713.jpg!50x50.png,community/20148/1410968142277-1410968147713
.jpg!30x30.png","group_ids":null,"name_pinyin":null,"screenname_pinyin":null,"photo_domain":"//xavatar
.imedao.com/"},"performance":{"top_gainer_symbol":"02007","top_gainer_name":"碧桂园","gain_count":3,"loss_count"
:1},"closed_at":null,"badges_exist":false,"sell_rebalancing":{"id":26370588,"status":"success","cube_id"
:888784,"prev_bebalancing_id":26023383,"category":"user_rebalancing","exe_strategy":"intraday_all","created_at"
:1492052968624,"updated_at":1492052968624,"cash_value":2.2e-7,"cash":0,"error_code":null,"error_message"
:"你上一笔调仓已成交。","error_status":null,"holdings":null,"rebalancing_histories":[{"id":146350520,"rebalancing_id"
:26370588,"stock_id":1004708,"stock_name":"海尔电器","stock_symbol":"01169","volume":0.02226274,"price":18
.1,"net_value":0.403,"weight":24,"target_weight":24,"prev_weight":25,"prev_target_weight":25,"prev_weight_adjusted"
:23.94,"prev_volume":0.02220298,"prev_price":18.72,"prev_net_value":0.41563978,"proactive":true,"created_at"
:1492052968624,"updated_at":1492052968624,"target_volume":0.02226274,"prev_target_volume":0.02220298
},{"id":146350521,"rebalancing_id":26370588,"stock_id":1004981,"stock_name":"碧桂园","stock_symbol":"02007"
,"volume":0.06027115,"price":7.8,"net_value":0.4701,"weight":28,"target_weight":28,"prev_weight":25,"prev_target_weight"
:25,"prev_weight_adjusted":27.35,"prev_volume":0.05887249,"prev_price":7.06,"prev_net_value":0.41563977
,"proactive":true,"created_at":1492052968624,"updated_at":1492052968624,"target_volume":0.06027115,"prev_target_volume"
:0.05887249},{"id":146350522,"rebalancing_id":26370588,"stock_id":1005109,"stock_name":"天虹纺织","stock_symbol"
:"02678","volume":0.07932199,"price":10.16,"net_value":0.8059,"weight":48,"target_weight":48,"prev_weight"
:30,"prev_target_weight":30,"prev_weight_adjusted":28.91,"prev_volume":0.04777469,"prev_price":10.44
,"prev_net_value":0.49876776,"proactive":true,"created_at":1492052968624,"updated_at":1492052968624,"target_volume"
:0.07932199,"prev_target_volume":0.04777469}],"comment":"","diff":19.8,"new_buy_count":0,"updated_at_format"
:"2017.4.13 11:09"},"created_date":"2016.06.11","created_date_format":"2016-06-11","close_date":"","authorized_visible"
:true};

SNB.cubePieData = [{"name":"家庭电器及用品","weight":24.61,"color":"#82b952"},{"name":"地产","weight":27.48,"color"
:"#d9633b"},{"name":"纺织、服饰及个人护理","weight":47.91,"color":"#e05173"}];

SNB.cubeTreeData = {"纺织、服饰及个人护理":{"name":"纺织、服饰及个人护理","weight":47.91,"color":"#e05173","stocks":[{"stock_id"
:1005109,"weight":47.91,"segment_name":"纺织、服饰及个人护理","segment_id":4739441,"stock_name":"天虹纺织","stock_symbol"
:"02678","segment_color":"#e05173","proactive":false,"volume":0.08138643,"textname":"undefined(02678
)","url":"/S/02678"}]},"地产":{"name":"地产","weight":27.48,"color":"#d9633b","stocks":[{"stock_id":1004981
,"weight":27.48,"segment_name":"地产","segment_id":4878950,"stock_name":"碧桂园","stock_symbol":"02007","segment_color"
:"#d9633b","proactive":false,"volume":0.06027115,"textname":"undefined(02007)","url":"/S/02007"}]},"
家庭电器及用品":{"name":"家庭电器及用品","weight":24.61,"color":"#82b952","stocks":[{"stock_id":1004708,"weight":24
.61,"segment_name":"家庭电器及用品","segment_id":4739440,"stock_name":"海尔电器","stock_symbol":"01169","segment_color"
:"#82b952","proactive":false,"volume":0.02226274,"textname":"undefined(01169)","url":"/S/01169"}]}};

SNB.marketInfo = "{\"sp_pamid\":[{\"param\":\"dimension\",\"filter_values\":[{\"name\":\"总收益排行（沪深）\"
,\"value\":\"annual\"},{\"name\":\"月排行（沪深）\",\"value\":\"month\"},{\"name\":\"周排行（沪深）\",\"value\":\"daily
\"}]}],\"updateTime\":1470105561000,\"hk\":[{\"param\":\"dimension\",\"filter_values\":[{\"name\":\"
总收益排行（港股）\",\"value\":\"annual\"},{\"name\":\"月收益排行（港股）\",\"value\":\"month\"},{\"name\":\"日收益排行（港股）
\",\"value\":\"daily\"}]}],\"cn\":[{\"param\":\"dimension\",\"filter_values\":[{\"name\":\"总收益排行（沪深）
\",\"value\":\"annual\"},{\"name\":\"月收益排行（沪深）\",\"value\":\"month\"},{\"name\":\"日收益排行（沪深）\",\"value
\":\"daily\"}]}],\"us\":[{\"param\":\"dimension\",\"filter_values\":[{\"name\":\"总收益排行（美股）\",\"value
\":\"annual\"},{\"name\":\"月收益排行（美股）\",\"value\":\"month\"},{\"name\":\"日收益排行（美股）\",\"value\":\"daily
\"}]}]}";
'''