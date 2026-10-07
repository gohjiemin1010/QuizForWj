import streamlit as st
import base64
import os
import time                                       
import streamlit.components.v1 as components      

# --- 核心改造：全局音频与悬浮控制按钮系统 ---
def get_audio_b64(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def init_audio_system():
    # 读取所有音频文件（新增了 clap.mp3）
    bgm_b64 = get_audio_b64("bgm.mp3")
    correct_b64 = get_audio_b64("correct.mp3")
    wrong_b64 = get_audio_b64("wrong.mp3")
    clap_b64 = get_audio_b64("clap.mp3")

    # 注入全局 JavaScript 来管理所有声音和右上角的按钮
    js_code = f"""
        <script>
            // 确保只初始化一次
            if (!window.parent.audioSystemInitialized) {{
                window.parent.audioSystemInitialized = true;
                window.parent.isMuted = false;

                // 1. 设置背景音乐
                var bgm = new Audio('data:audio/mp3;base64,{bgm_b64}');
                bgm.loop = true;
                window.parent.bgmAudio = bgm;

                // 2. 提供给 Python 调用的音效播放函数 (支持三种音效)
                window.parent.playSfx = function(type) {{
                    if (window.parent.isMuted) return; // 如果静音了就不播放

                    var b64_data = '';
                    if (type === 'correct') b64_data = '{correct_b64}';
                    else if (type === 'wrong') b64_data = '{wrong_b64}';
                    else if (type === 'clap') b64_data = '{clap_b64}';

                    if (b64_data) {{
                        var sfx = new Audio('data:audio/mp3;base64,' + b64_data);
                        sfx.play().catch(e => console.log("音效播放被拦截:", e));
                    }}
                }};

                // 3. 在右上角创建一个悬浮的静音按钮
                var btn = window.parent.document.createElement('button');
                btn.innerHTML = '🔊 声音: 开';
                btn.style.position = 'fixed';
                btn.style.top = '25px';
                btn.style.right = '25px';
                btn.style.zIndex = '999999'; 
                btn.style.padding = '8px 16px';
                btn.style.fontSize = '14px';
                btn.style.fontWeight = 'bold';
                btn.style.backgroundColor = '#ffffff';
                btn.style.color = '#5c4033';
                btn.style.border = '2px solid #deb887';
                btn.style.borderRadius = '20px';
                btn.style.cursor = 'pointer';
                btn.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                btn.style.transition = 'all 0.2s';

                btn.onmouseover = function() {{ btn.style.transform = 'scale(1.05)'; }};
                btn.onmouseout = function() {{ btn.style.transform = 'scale(1)'; }};

                btn.onclick = function() {{
                    window.parent.isMuted = !window.parent.isMuted;
                    if (window.parent.isMuted) {{
                        window.parent.bgmAudio.pause();
                        btn.innerHTML = '🔇 声音: 关';
                        btn.style.backgroundColor = '#ffe4e1'; 
                    }} else {{
                        window.parent.bgmAudio.play();
                        btn.innerHTML = '🔊 声音: 开';
                        btn.style.backgroundColor = '#ffffff';
                    }}
                }};
                window.parent.document.body.appendChild(btn);

                // 4. 用户点击页面任意位置时，尝试播放BGM
                window.parent.document.body.addEventListener('click', function() {{
                    if (!window.parent.isMuted && window.parent.bgmAudio.paused && '{bgm_b64}') {{
                        window.parent.bgmAudio.play().catch(e => console.log("BGM播放仍被拦截"));
                    }}
                }}, {{ once: true }});
            }}
        </script>
    """
    components.html(js_code, height=0, width=0)

# --- 触发音效的函数 ---
def trigger_sfx(is_correct):
    sfx_type = "correct" if is_correct else "wrong"
    js = f"<script>if(window.parent.playSfx) window.parent.playSfx('{sfx_type}');</script>"
    components.html(js, height=0, width=0)

# --- 背景图片及核心样式设置 ---
# --- 背景图片及核心样式设置 ---
def add_bg_from_local(image_file):
    if not os.path.exists(image_file):
        return 

    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
    f"""
    <style>
    /* 1. 全局背景 */
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)), url(data:image/jpg;base64,{encoded_string});
        background-size: cover;          
        background-position: center;     
        background-attachment: fixed;    
    }}

    /* 2. 悬浮大方块 */
    .block-container {{
        background: linear-gradient(145deg, rgba(255, 253, 240, 0.95), rgba(250, 240, 215, 0.95)) !important; 
        border-radius: 25px; 
        padding: 3rem !important; 
        max-width: 850px !important;
        margin-top: 22vh !important; 
        margin-bottom: 10vh !important;
        margin-left: auto !important;
        margin-right: auto !important;
        box-shadow: 0 10px 20px rgba(139, 115, 85, 0.15), 0 6px 6px rgba(139, 115, 85, 0.1), inset 0 -5px 0 rgba(139, 115, 85, 0.05);
        transition: all 0.3s ease-in-out;
    }}
    .block-container:hover {{
        transform: translateY(-8px); 
        box-shadow: 0 22px 30px rgba(139, 115, 85, 0.2), 0 10px 10px rgba(139, 115, 85, 0.15), inset 0 -5px 0 rgba(139, 115, 85, 0.05); 
    }}

    /* 3. 按钮配色优化 */
    div[data-testid="stButton"] button {{
        background-color: #ffffff !important;
        border: 2px solid #deb887 !important; 
        color: #5c4033 !important; 
        font-weight: 800 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }}
    div[data-testid="stButton"] button:hover {{
        border-color: #d2691e !important; 
        color: #d2691e !important;
        transform: translateY(-3px); 
        box-shadow: 0 6px 12px rgba(210, 105, 30, 0.2);
    }}

    /* 4. 💖 完美修复版：只针对具体的选项进行满宽改造，放过标题 💖 */
    /* 强制容器全宽 */
    div[data-testid="stRadio"],
    div[data-testid="stRadio"] > div,
    div[role="radiogroup"] {{
        width: 100% !important;
    }}

    /* 核心修复：使用 [role="radiogroup"] 确保绝对不会误伤上面那句"请选择你的答案" */
    div[role="radiogroup"] label {{
        background: linear-gradient(to right, #fdf9f1, #f5ebd3) !important;
        border: 2px solid #e3d2be !important;
        border-radius: 15px !important;
        padding: 16px 24px !important; 
        cursor: pointer !important;
        box-shadow: 0 4px 6px rgba(139, 115, 85, 0.05) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important; 
        display: flex !important;
        align-items: center !important;
        box-sizing: border-box !important; 
        margin-bottom: 12px !important; /* 强制增加保底间距，防止选项贴在一起 */
    }}

    div[role="radiogroup"] label:hover {{
        background: #fcf1da !important;
        border-color: #d2691e !important;
        transform: translateX(8px) !important; 
        box-shadow: 0 6px 12px rgba(210, 105, 30, 0.15) !important;
    }}

    /* 选中状态下的高亮反馈 */
    div[role="radiogroup"] label:has(input:checked) {{
        background: #fae6c5 !important;
        border: 2px solid #d2691e !important;
        box-shadow: 0 0 12px rgba(210, 105, 30, 0.2) !important;
        transform: translateX(8px) !important; 
    }}

    /* 彻底隐藏掉原本那颗圆圆的单选按钮 */
    div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}

    /* 文字排版优化，保证文字在方块里好看且不会被压缩 */
    div[role="radiogroup"] p {{
        font-size: 1.15rem !important;
        font-weight: bold !important;
        color: #5c4033 !important;
        margin: 0 !important;
        width: 100% !important; 
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

# --- 页面配置 ---
st.set_page_config(page_title="五年级历史大挑战", page_icon="👑", layout="centered")

# 初始化背景和全局音频系统
add_bg_from_local('bg1.jpg')
init_audio_system()

# --- 1. 题库数据 ---
quiz_data = {
    1: [
        {"question": "以下哪个州属的君主使用“拉惹”的称号?", "options": ["吉兰丹", "森美兰", "玻璃市"], "answer": "玻璃市"},
        {"question": "森美兰州的君主被称为？", "options": ["苏丹", "最高统治者 (Yang di-Pertuan Besar)", "州元首"], "answer": "最高统治者 (Yang di-Pertuan Besar)"},
        {"question": "马来西亚目前共有多少个州属是由苏丹、拉惹或最高统治者统治？", "options": ["9 个", "11 个", "14 个"], "answer": "9 个"},
        {"question": "以下哪个州属没有君主，而是由州元首（Yang di-Pertua Negeri）担任州首长？", "options": ["彭亨", "马六甲", "霹雳"], "answer": "马六甲"},
        {"question": "在古代马来社会，君主的地位是什么？", "options": ["处于社会阶级的最高端", "和普通平民一样", "负责耕种的阶级"], "answer": "处于社会阶级的最高端"},
        {"question": "“背叛 (Derhaka)” 在古代马来社会的意思是？", "options": ["人民对君主的忠心", "人民违逆拉惹或苏丹的命令", "国家之间的战争"], "answer": "人民违逆拉惹或苏丹的命令"},
        {"question": "“哇迪亚 (Waadat)” 是指谁和谁之间的誓约？", "options": ["统治者与人民", "英国人和马来人", "马来西亚和新加坡"], "answer": "统治者与人民"},
        {"question": "我国的“国家元首”是由谁推选出来的？", "options": ["人民投票选出", "马来统治者理事会", "英国国王任命"], "answer": "马来统治者理事会"},
        {"question": "以下哪个东南亚国家至今依然实行“君主制度”？", "options": ["新加坡", "泰国", "印度尼西亚"], "answer": "泰国"},
        {"question": "我国目前实行的是什么制度，意味着君主的权力受到宪法的限制？", "options": ["君主专制", "共和国制", "君主立宪制"], "answer": "君主立宪制"},
    ],
    2: [
        {"question": "根据《联邦宪法》，马来西亚的联邦宗教是什么？", "options": ["佛教", "基督教", "伊斯兰教"], "answer": "伊斯兰教"},
        {"question": "伊斯兰教大约是在什么时期传入马来半岛的？", "options": ["马六甲王朝时期", "英国殖民时期", "日本占领时期"], "answer": "马六甲王朝时期"},
        {"question": "以下哪一项文物证明了伊斯兰教在早期已经传入登嘉楼？", "options": ["汉都亚的短剑", "登嘉楼史迹碑", "马六甲古城门"], "answer": "登嘉楼史迹碑"},
        {"question": "虽然伊斯兰教是联邦宗教，但我国人民享有信仰其他宗教的自由吗？", "options": ["不可以，必须信奉伊斯兰教", "可以，人民有宗教信仰自由", "只能信仰两种宗教"], "answer": "可以，人民有宗教信仰自由"},
        {"question": "在有君主的州属（如柔佛、吉打），谁是该州的伊斯兰教首长？", "options": ["首相", "苏丹 / 统治者", "国家元首"], "answer": "苏丹 / 统治者"},
        {"question": "在没有君主的州属（如槟城、沙巴），谁是该州的伊斯兰教首长？", "options": ["国家元首", "州元首", "首相"], "answer": "国家元首"},
        {"question": "为了维持社会秩序，马六甲王朝时期制定了哪部包含伊斯兰教义的法律？", "options": ["《马六甲法典》", "《汉都亚传》", "《马来纪年》"], "answer": "《马六甲法典》"},
        {"question": "伊斯兰教的传入，让马六甲成为了当时的什么中心？", "options": ["农业种植中心", "伊斯兰教的传播与教育中心", "制造武器中心"], "answer": "伊斯兰教的传播与教育中心"},
        {"question": "作为穆斯林，必须履行的“五功”之一是什么？", "options": ["斋戒 (Puasa)", "练武术", "出海打渔"], "answer": "斋戒 (Puasa)"},
        {"question": "伊斯兰教提倡的生活价值观之一是什么？", "options": ["互相争吵", "和平与互相尊重", "欺负弱小"], "answer": "和平与互相尊重"},
    ],
    3: [
        {"question": "马来西亚的国语和官方语言是什么语言？", "options": ["英语", "华语", "马来语"], "answer": "马来语"},
        {"question": "马来语源自于世界上的哪个语系？", "options": ["印欧语系", "南岛语系", "汉藏语系"], "answer": "南岛语系"},
        {"question": "在马六甲王朝时期，马来语扮演了什么重要角色，让各国商人都能沟通？", "options": ["通用语言 (Lingua Franca)", "秘密语言", "宗教语言"], "answer": "通用语言 (Lingua Franca)"},
        {"question": "早期在还没有罗马字母（ABC）时，马来语主要使用什么文字书写？", "options": ["爪夷文 (Jawi)", "梵文", "象形文字"], "answer": "爪夷文 (Jawi)"},
        {"question": "我国设立了哪个官方机构，专门负责发展和巩固马来语的地位？", "options": ["国家博物馆", "国家语文局 (DBP)", "旅游局"], "answer": "国家语文局 (DBP)"},
        {"question": "哪项法令正式确立了马来语作为我国国语和官方语言的地位？", "options": ["《1957年独立法令》", "《1963/67年国语法令》", "《交通法令》"], "answer": "《1963/67年国语法令》"},
        {"question": "有一位著名的学者对马来语的语法和发展做出了巨大贡献，他是谁？", "options": ["东姑阿都拉曼", "再那阿比丁 (Za'ba)", "比南利 (P. Ramlee)"], "answer": "再那阿比丁 (Za'ba)"},
        {"question": "以下哪一个地方必须使用马来语作为主要的官方沟通语言？", "options": ["私人朋友聚会", "政府部门和法庭", "国外的快餐店"], "answer": "政府部门和法庭"},
        {"question": "为什么我们要重视并且学好国语？", "options": ["为了促进各族人民的团结", "为了可以去英国留学", "为了方便玩电子游戏"], "answer": "为了促进各族人民的团结"},
        {"question": "如果在政府学校集会时要致辞，通常会优先使用什么语言？", "options": ["马来语", "英语", "泰米尔语"], "answer": "马来语"},
    ],
    4: [
        {"question": "在 1511 年，哪个欧洲势力最早占领了马六甲？", "options": ["荷兰", "葡萄牙", "英国"], "answer": "葡萄牙"},
        {"question": "荷兰人占领马六甲的主要目的是什么？", "options": ["控制香料贸易", "学习马来语", "帮助当地人建皇宫"], "answer": "控制香料贸易"},
        {"question": "英国人詹姆斯·布洛克 (James Brooke) 统治了马来西亚的哪个地区？", "options": ["沙巴", "槟城", "砂拉越"], "answer": "砂拉越"},
        {"question": "英国北婆罗洲公司 (SBUB) 统治了哪个地区？", "options": ["沙巴", "马六甲", "柔佛"], "answer": "沙巴"},
        {"question": "英国人最初是为了掠夺什么天然资源，而开始干涉霹雳州的内政？", "options": ["黄金", "锡矿", "石油"], "answer": "锡矿"},
        {"question": "什么是“参政司” (Residen) 制度？", "options": ["英国人当苏丹", "苏丹必须听取英国顾问的建议（除了宗教与风俗）", "英国人负责种田"], "answer": "苏丹必须听取英国顾问的建议（除了宗教与风俗）"},
        {"question": "第二次世界大战期间，哪个外来势力占领了马来亚长达三年零八个月？", "options": ["日本", "英国", "暹罗 (泰国)"], "answer": "日本"},
        {"question": "外来势力为什么对我国感兴趣？", "options": ["我国有很多高楼大厦", "我国有丰富的天然资源和优越的地理位置", "为了来度假"], "answer": "我国有丰富的天然资源和优越的地理位置"},
        {"question": "在槟城，英国的法兰西斯·莱特 (Francis Light) 占领该岛后将其改名为什么？", "options": ["威尔斯太子岛", "维多利亚岛", "乔治市"], "answer": "威尔斯太子岛"},
        {"question": "外来势力的干涉给我国带来了什么影响？", "options": ["我国完全没有改变", "导致我国人民失去权力，财富被掠夺", "苏丹的权力变得更大"], "answer": "导致我国人民失去权力，财富被掠夺"},
    ],
    5: [
        {"question": "在霹雳州，谁因为反抗英国参政司毕治 (J.W.W. Birch) 的不公平政策而奋斗？", "options": ["拿督马哈拉惹里拉", "多赛德", "仁答"], "answer": "拿督马哈拉惹里拉"},
        {"question": "多赛德 (Dol Said) 是哪个地区的地方领袖，他成功打败了英国人的第一次进攻？", "options": ["彭亨", "南宁 (Naning)", "沙巴"], "answer": "南宁 (Naning)"},
        {"question": "砂拉越的抗英英雄仁答 (Rentap) 著名的战斗口号 “Agi Idup, Agi Ngelaban” 是什么意思？", "options": ["只要一息尚存，就要反抗到底", "团结就是力量", "和平万岁"], "answer": "只要一息尚存，就要反抗到底"},
        {"question": "末沙烈 (Mat Salleh) 是哪个州属著名的反英领袖？", "options": ["沙巴", "登嘉楼", "砂拉越"], "answer": "沙巴"},
        {"question": "吉兰丹州的著名反英领袖督江格 (Tok Janggut) 反抗英国人的主要原因是什么？", "options": ["他想当苏丹", "反对英国人实行的税务制度", "反对建造铁路"], "answer": "反对英国人实行的税务制度"},
        {"question": "彭亨州反抗英国人的著名领袖是谁？", "options": ["拿督巴哈曼 (Dato' Bahaman)", "哈芝阿都拉曼", "安德南"], "answer": "拿督巴哈曼 (Dato' Bahaman)"},
        {"question": "登嘉楼州的哈芝阿都拉曼林梦反抗英国人的原因是什么？", "options": ["反对英国人的土地法，认为土地属于上苍", "反对开采金矿", "反对英国人建学校"], "answer": "反对英国人的土地法，认为土地属于上苍"},
        {"question": "砂拉越的另一位著名领袖莎里夫马沙荷 (Sharif Masahor) 反抗了谁的统治？", "options": ["荷兰人", "日本人", "詹姆斯·布洛克家族"], "answer": "詹姆斯·布洛克家族"},
        {"question": "这些地方领袖抗争的共同特征是什么？", "options": ["为了个人的荣华富贵", "保卫家园，反抗殖民者的压迫与不公", "为了抢夺其他州的土地"], "answer": "保卫家园，反抗殖民者的压迫与不公"},
        {"question": "作为后代，我们应该向这些抗争领袖学习什么精神？", "options": ["贪生怕死", "勇敢和爱国精神", "自私自利"], "answer": "勇敢和爱国精神"},
    ],
    6: [
        {"question": "我国在什么日期正式宣布独立？", "options": ["1957年8月31日", "1963年9月16日", "1945年8月15日"], "answer": "1957年8月31日"},
        {"question": "谁是我国的第一任首相，被称为“独立之父”？", "options": ["敦马哈迪", "东姑阿都拉曼", "敦拉萨"], "answer": "东姑阿都拉曼"},
        {"question": "宣布独立的仪式是在吉隆坡的哪个地方举行的？", "options": ["国家皇宫", "双峰塔", "默迪卡体育场 (Stadium Merdeka)"], "answer": "默迪卡体育场 (Stadium Merdeka)"},
        {"question": "在争取独立的过程中，我国代表团去哪个国家进行最终谈判？", "options": ["日本东京", "英国伦敦", "美国华盛顿"], "answer": "英国伦敦"},
        {"question": "在宣布独立时，东姑阿都拉曼带领群众高喊了多少次“Merdeka”？", "options": ["3次", "7次", "10次"], "answer": "7次"},
        {"question": "为了对抗马来亚共产党的威胁，英国政府宣布马来亚进入什么状态？", "options": ["紧急状态 (Darurat)", "戒严状态", "和平状态"], "answer": "紧急状态 (Darurat)"},
        {"question": "在争取独立时，哪一个由三大民族组成的政党联盟发挥了核心作用？", "options": ["联盟 (Parti Perikatan)", "反对党", "大马阵线"], "answer": "联盟 (Parti Perikatan)"},
        {"question": "1957年8月30日午夜12点，在独立广场降下的是什么旗帜？", "options": ["日本国旗", "英国国旗 (Union Jack)", "荷兰国旗"], "answer": "英国国旗 (Union Jack)"},
        {"question": "“Merdeka” 这个词代表着什么意思？", "options": ["和平", "独立与自由", "国家繁荣"], "answer": "独立与自由"},
        {"question": "作为马来西亚的子民，我们应该如何捍卫国家的独立？", "options": ["不关心国家大事", "破坏公共设施", "互相尊重，保持各族团结"], "answer": "互相尊重，保持各族团结"},
    ],
    7: [
        {"question": "国家最高元首是我国的最高领导人，他的任期是几年？", "options": ["3年", "5年", "终身制"], "answer": "5年"},
        {"question": "最高元首是由谁推选出来的？", "options": ["人民投票选举", "首相任命", "马来统治者理事会"], "answer": "马来统治者理事会"},
        {"question": "我国最高元首是由几个州的马来统治者轮流担任的？", "options": ["9个", "11个", "13个"], "answer": "9个"},
        {"question": "国家最高元首在行使行政职权时，必须听取谁的建议？", "options": ["首相与内阁", "法官", "州元首"], "answer": "首相与内阁"},
        {"question": "国家最高元首的官方住所叫什么？", "options": ["首相署", "国家皇宫 (Istana Negara)", "国家议会"], "answer": "国家皇宫 (Istana Negara)"},
        {"question": "以下哪一项是国家最高元首的权力之一？", "options": ["批改学生的考试考卷", "委任首相及内阁部长", "决定百货公司的商品价格"], "answer": "委任首相及内阁部长"},
        {"question": "除了担任国家领袖，最高元首也是我国哪个部队的最高统帅？", "options": ["警察部队", "国家武装部队 (海陆空军)", "消防部队"], "answer": "国家武装部队 (海陆空军)"},
        {"question": "如果国家最高元首想要提前退位，他需要向谁呈交辞职信？", "options": ["马来统治者理事会", "首相", "联合国"], "answer": "马来统治者理事会"},
        {"question": "国家最高元首的妻子拥有的官方称号是什么？", "options": ["最高元首后 (Raja Permaisuri Agong)", "苏丹后", "首相夫人"], "answer": "最高元首后 (Raja Permaisuri Agong)"},
        {"question": "为什么我们要尊敬国家最高元首？", "options": ["因为他是国家主权、团结与和平的象征", "因为他规定我们必须这么做", "因为他颁发奖学金"], "answer": "因为他是国家主权、团结与和平的象征"},
    ],
    8: [
        {"question": "国徽盾牌上方有“五把马来短剑”，它们代表什么？", "options": ["前马来属邦的五个州", "国家的五位将军", "五大民族"], "answer": "前马来属邦的五个州"},
        {"question": "国徽中间有红、黑、白、黄四种颜色，代表前马来联邦，其中包括哪四个州属？", "options": ["玻璃市、吉打、吉兰丹、登嘉楼", "彭亨、雪兰莪、霹雳、森美兰", "沙巴、砂拉越、槟城、马六甲"], "answer": "彭亨、雪兰莪、霹雳、森美兰"},
        {"question": "国徽左右两侧有两只老虎，老虎在我国代表什么？", "options": ["勇敢与力量", "聪明与智慧", "和平与安静"], "answer": "勇敢与力量"},
        {"question": "国徽最顶端的十四角星代表什么？", "options": ["马来西亚的13个州属和联邦直辖区", "14位英雄", "14个节日"], "answer": "马来西亚的13个州属和联邦直辖区"},
        {"question": "国徽最顶端的新月（月亮）代表什么？", "options": ["伊斯兰教是联邦宗教", "夜晚的宁静", "农业的丰收"], "answer": "伊斯兰教是联邦宗教"},
        {"question": "国徽下方有一条黄色的横幅，上面用罗马字母和爪夷文写着什么国家标语？", "options": ["马来西亚能 (Malaysia Boleh)", "团结就是力量 (Bersekutu Bertambah Mutu)", "和平万岁"], "answer": "团结就是力量 (Bersekutu Bertambah Mutu)"},
        {"question": "国徽盾牌左侧的“槟榔树和槟威大桥”代表哪个州？", "options": ["马六甲", "槟城", "砂拉越"], "answer": "槟城"},
        {"question": "国徽盾牌右侧的“马六甲树”代表哪个州？", "options": ["马六甲", "柔佛", "彭亨"], "answer": "马六甲"},
        {"question": "国徽下方的三个小格子里，左边是沙巴州徽，右边是砂拉越州徽，中间的大红花代表什么？", "options": ["我国的国花", "美丽的风景", "丰富的农业"], "answer": "我国的国花"},
        {"question": "作为国民，我们应该如何看待国徽？", "options": ["觉得它只是一个图案", "尊敬它，因为它是国家主权与尊严的象征", "随意涂改它的颜色"], "answer": "尊敬它，因为它是国家主权与尊严的象征"},
    ],
    9: [
        {"question": "马来西亚的国旗叫什么名字？", "options": ["辉煌条纹 (Jalur Gemilang)", "独立之旗", "团结旗"], "answer": "辉煌条纹 (Jalur Gemilang)"},
        {"question": "国旗上一共有多少道红白相间的条纹？", "options": ["11道", "13道", "14道"], "answer": "14道"},
        {"question": "国旗上的黄色代表什么？", "options": ["君主立宪制与皇室", "黄金和财富", "太阳的光芒"], "answer": "君主立宪制与皇室"},
        {"question": "国旗上的红色代表什么？", "options": ["危险", "勇敢", "热情"], "answer": "勇敢"},
        {"question": "国旗上的深蓝色代表什么？", "options": ["海洋", "各族人民团结一致", "广阔的天空"], "answer": "各族人民团结一致"},
        {"question": "国旗上的白色代表什么？", "options": ["纯洁与诚实", "和平的鸽子", "云朵"], "answer": "纯洁与诚实"},
        {"question": "国旗的十四角星和十四道条纹代表什么？", "options": ["13个州属与联邦直辖区的团结", "14个不同的民族", "14位历任首相"], "answer": "13个州属与联邦直辖区的团结"},
        {"question": "马来亚联合邦第一面国旗的设计者是谁？", "options": ["东姑阿都拉曼", "莫哈末韩查 (Mohamad bin Hamzah)", "敦马哈迪"], "answer": "莫哈末韩查 (Mohamad bin Hamzah)"},
        {"question": "“辉煌条纹”这个名字是由哪位首相在1997年宣布的？", "options": ["第二任首相敦拉萨", "第四任首相敦马哈迪", "第一任首相东姑阿都拉曼"], "answer": "第四任首相敦马哈迪"},
        {"question": "如果国旗破损或褪色了，我们应该怎么做？", "options": ["当作垃圾丢掉", "拿来当抹布", "妥善地销毁，不可随意丢弃"], "answer": "妥善地销毁，不可随意丢弃"},
    ],
    10: [
        {"question": "马来西亚的国歌名字是什么？", "options": ["我的国家 (Negaraku)", "祖国母亲", "团结的马来西亚"], "answer": "我的国家 (Negaraku)"},
        {"question": "我国国歌的曲调是改编自哪个州的州歌？", "options": ["柔佛州", "霹雳州", "雪兰莪州"], "answer": "霹雳州"},
        {"question": "当听到正在播放国歌时，我们应该保持什么姿势？", "options": ["坐着继续聊天", "肃立，双手垂直贴紧大腿", "随处走动"], "answer": "肃立，双手垂直贴紧大腿"},
        {"question": "谁是负责挑选和确认国歌歌词的委员会主席？", "options": ["东姑阿都拉曼", "敦阿都拉萨", "敦胡先翁"], "answer": "东姑阿都拉曼"},
        {"question": "国歌歌词中“Rakyat hidup bersatu dan maju” 的意思是什么？", "options": ["人民生活团结与进步", "人民永远健康", "国家充满财富"], "answer": "人民生活团结与进步"},
        {"question": "如果迟到学校，走到校门时刚好正在播放国歌，你应该怎么做？", "options": ["马上跑进班里", "马上停下脚步，立正直到国歌结束", "蹲在路边"], "answer": "马上停下脚步，立正直到国歌结束"},
        {"question": "为什么我们要大声、充满感情地唱国歌？", "options": ["为了吵醒别人", "为了培养爱国精神和对国家的忠诚", "为了练习唱歌"], "answer": "为了培养爱国精神和对国家的忠诚"},
        {"question": "故意不尊重国歌（如恶搞歌词）的人会面临什么后果？", "options": ["可能被警方逮捕并面临罚款或监禁", "只会被老师骂一顿", "没有任何后果"], "answer": "可能被警方逮捕并面临罚款或监禁"},
        {"question": "国歌的最后一句“Tuhan kurniakan, Raja kita selamat bertakhta” 祈求上苍保佑谁平安统治？", "options": ["首相", "君主 / 国王", "平民百姓"], "answer": "君主 / 国王"},
        {"question": "国歌在什么时候会被播放？", "options": ["每天吃晚餐时", "学校周会、国家庆典或健儿在国际比赛夺金时", "看电影中途"], "answer": "学校周会、国家庆典或健儿在国际比赛夺金时"},
    ],
    11: [
        {"question": "根据《联邦宪法》第152条文，什么语言被列为我国的国语？", "options": ["英语", "马来语", "华语"], "answer": "马来语"},
        {"question": "为了鼓励国民多使用国语，政府会在每年举办什么活动？", "options": ["国语月 (Bulan Bahasa Kebangsaan)", "英语周", "数学比赛"], "answer": "国语月 (Bulan Bahasa Kebangsaan)"},
        {"question": "马来语作为国语的核心目的之一是什么？", "options": ["为了取代所有的方言", "为了团结我国多元种族的社会", "为了与外国做生意"], "answer": "为了团结我国多元种族的社会"},
        {"question": "在法庭、政府部门处理官方事务时，规定的官方语言是什么？", "options": ["英语", "马来语", "泰米尔语"], "answer": "马来语"},
        {"question": "《国家教育政策》将哪种语言定为国民学校（Sekolah Kebangsaan）的主要教学媒介语？", "options": ["英语", "华语", "马来语"], "answer": "马来语"},
        {"question": "在多元种族的马来西亚，马来语在日常生活中最常扮演什么角色？", "options": ["各族人民之间的沟通语言", "只有在考试时才用的语言", "写诗专用的语言"], "answer": "各族人民之间的沟通语言"},
        {"question": "作为一个爱国的马来西亚人，我们可以通过什么方式表达对国语的骄傲？", "options": ["只在学校里用，出去就不说", "在日常生活中正确且礼貌地使用国语", "故意用错语法"], "answer": "在日常生活中正确且礼貌地使用国语"},
        {"question": "如果一位华裔和一位印裔邻居在巴刹相遇聊天，他们最可能使用什么语言沟通？", "options": ["马来语", "法语", "淡米尔语"], "answer": "马来语"},
        {"question": "以下哪项是错误使用国语的行为？", "options": ["在演讲时使用标准马来语发音", "在正式公文中混合使用粗俗方言", "写信给政府部门时使用马来语"], "answer": "在正式公文中混合使用粗俗方言"},
        {"question": "为什么很多路牌、政府公告和商业招牌都必须有马来语？", "options": ["因为马来语字母最少", "因为国语是国家的官方语言，代表国家特征", "因为看起来比较美观"], "answer": "因为国语是国家的官方语言，代表国家特征"},
    ],
    12: [
        {"question": "马来西亚的国花是什么？", "options": ["玫瑰花", "胡姬花", "大红花 (Bunga Raya)"], "answer": "大红花 (Bunga Raya)"},
        {"question": "哪一位首相在1960年正式宣布大红花为我国的国花？", "options": ["东姑阿都拉曼", "敦阿都拉萨", "敦马哈迪"], "answer": "东姑阿都拉曼"},
        {"question": "在选出国花之前，曾有哪几种花朵一起参与“竞选”？（选出正确的组合）", "options": ["向日葵、菊花", "茉莉花、莲花、玫瑰花", "郁金香、牡丹"], "answer": "茉莉花、莲花、玫瑰花"},
        {"question": "为什么大红花最终脱颖而出被选为国花？", "options": ["因为它最贵", "因为它颜色鲜艳，而且在我国随处可见，容易种植", "因为它只在冬天开花"], "answer": "因为它颜色鲜艳，而且在我国随处可见，容易种植"},
        {"question": "大红花那鲜艳夺目的红色象征着什么？", "options": ["勇敢、坚毅的国民精神", "危险的警告", "炎热的天气"], "answer": "勇敢、坚毅的国民精神"},
        {"question": "大红花一共有几个花瓣？", "options": ["3个", "4个", "5个"], "answer": "5个"},
        {"question": "大红花的5个花瓣，刚好代表了我国的什么国家理念？", "options": ["五大宗教", "五大种族", "国家原则 (Rukun Negara)"], "answer": "国家原则 (Rukun Negara)"},
        {"question": "以下哪一项属于五项“国家原则”之一？", "options": ["信奉上苍 (Kepercayaan kepada Tuhan)", "准时上学", "每天做运动"], "answer": "信奉上苍 (Kepercayaan kepada Tuhan)"},
        {"question": "我们在日常生活中，最常在哪个物品上看到大红花的图案？", "options": ["书包上", "硬币和纸钞 (钱币) 上", "汽车轮胎上"], "answer": "硬币和纸钞 (钱币) 上"},
        {"question": "把大红花作为国花，体现了国家希望人民能像这朵花一样怎么做？", "options": ["永远团结、和平及坚强", "安静地站在路边", "只在早上出现"], "answer": "永远团结、和平及坚强"},
    ]
}

# --- 2. 初始化游戏状态 (Session State) ---
if 'unlocked_level' not in st.session_state:
    st.session_state.unlocked_level = 1
if 'current_level' not in st.session_state:
    st.session_state.current_level = None
if 'question_queue' not in st.session_state:
    st.session_state.question_queue = []
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = False
if 'total_q_count' not in st.session_state:
    st.session_state.total_q_count = 0
if 'just_answered' not in st.session_state:
    st.session_state.just_answered = False
if 'just_completed' not in st.session_state:
    st.session_state.just_completed = False

# --- 3. 界面逻辑 ---

# 场景 A: 主菜单（关卡选择界面）
if st.session_state.current_level is None:

    st.title("🗺️ 五年级历史探险")
    st.markdown("欢迎来到历史探险！完成当前关卡的所有挑战，才能解锁下一关哦！")

    cols = st.columns(3)
    for level in range(1, 13):
        col_idx = (level - 1) % 3
        with cols[col_idx]:
            if level <= st.session_state.unlocked_level:
                if st.button(f"🔓 单元 {level}", key=f"lvl_{level}", use_container_width=True):
                    if level in quiz_data and len(quiz_data[level]) > 0:
                        st.session_state.current_level = level
                        st.session_state.question_queue = list(quiz_data[level])
                        st.session_state.total_q_count = len(quiz_data[level])
                        st.session_state.answered = False
                        st.session_state.level_start_time = time.time()
                        st.session_state.just_completed = False
                        st.rerun()
                    else:
                        st.warning("🚧 还在努力更新这个单元的题目哦！")
            else:
                st.button(f"🔒 单元 {level} (未解锁)", key=f"lvl_{level}", disabled=True, use_container_width=True)

# 场景 B: 答题界面
else:
    if len(st.session_state.question_queue) > 0:
        current_level = st.session_state.current_level
        q = st.session_state.question_queue[0] 

        # --- 顶部排版：左边标题，右边计时器 ---
        col_title, col_timer = st.columns([1, 1])

        with col_title:
            st.markdown(f"### ⚔️ 单元 {current_level} 挑战中")

        with col_timer:
            if 'level_start_time' not in st.session_state:
                st.session_state.level_start_time = time.time()

            start_t = st.session_state.level_start_time
            components.html(f"""
                <style>body {{ margin: 0; background: transparent; overflow: hidden; }}</style>
                <div id="timer" style="font-family: 'Segoe UI', sans-serif; font-size: 1.2rem; font-weight: 800; color: #d2691e; padding-top: 12px; text-align: right; padding-right: 15px;">
                    ⏱️ 用时 00:00
                </div>
                <script>
                    var startTime = {start_t};
                    function updateTimer() {{
                        var diff = Math.floor((Date.now() / 1000) - startTime);
                        var m = Math.floor(diff / 60).toString().padStart(2, '0');
                        var s = (diff % 60).toString().padStart(2, '0');
                        document.getElementById('timer').innerText = '⏱️ 用时 ' + m + ':' + s;
                    }}
                    setInterval(updateTimer, 1000); 
                    updateTimer();
                </script>
            """, height=45)

        # --------------------------------------------------------

        remaining = len(st.session_state.question_queue)
        st.info(f"加油！还有 **{remaining}** 道题需要答对才能过关！")

        st.markdown(f"### {q['question']}")

        user_choice = st.radio("请选择你的答案：", q['options'], key="current_radio")

        # --- 显示答题反馈提示语，并触发答对/错音效 ---
        if st.session_state.answered:
            if st.session_state.is_correct:
                st.success("🎉 太棒了！回答正确！")
                if st.session_state.just_answered:
                    trigger_sfx(True)
                    st.session_state.just_answered = False
            else:
                st.error(f"💔 哎呀，答错了！正确答案是: **{q['answer']}**")
                st.warning("没关系，这道题等一下会重新出现，直到你记住为止哦！")
                if st.session_state.just_answered:
                    trigger_sfx(False)
                    st.session_state.just_answered = False

        # 制造一点空白间隔
        st.markdown("<br>", unsafe_allow_html=True)

        # --- 底部排版：左边返回地图，右边操作按钮(提交/下一题) ---
        col_back, col_action = st.columns(2)

        with col_back:
            if st.button("🏠 返回主页", use_container_width=True):
                st.session_state.current_level = None
                if 'level_start_time' in st.session_state:
                    del st.session_state['level_start_time']
                st.rerun()

        with col_action:
            if not st.session_state.answered:
                if st.button("🚀 提交答案", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.just_answered = True

                    if user_choice == q['answer']:
                        st.session_state.is_correct = True
                    else:
                        st.session_state.is_correct = False
                    st.rerun()
            else:
                if st.button("下一题 ➡️", use_container_width=True):
                    processed_q = st.session_state.question_queue.pop(0)
                    if not st.session_state.is_correct:
                        st.session_state.question_queue.append(processed_q)

                    st.session_state.answered = False

                    # 核心逻辑：如果点完下一题发现队列空了，代表刚好通关了！
                    if len(st.session_state.question_queue) == 0:
                        st.session_state.just_completed = True

                    st.rerun()

    # 场景 C: 关卡完成界面
    else:
        # 当刚刚通关时，同时触发原生热气球、掌声音效、和绚丽的满屏放炮（礼花）
        if st.session_state.get('just_completed', False):
            st.balloons() 

            # 注入炫酷的前端放炮(Confetti)特效和鼓掌声音
            confetti_and_clap_js = """
                <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
                <script>
                    // 1. 播放掌声
                    if (window.parent.playSfx) window.parent.playSfx('clap');

                    // 2. 放礼花特效
                    var duration = 4 * 1000;
                    var end = Date.now() + duration;
                    (function frame() {
                        confetti({
                            particleCount: 8,
                            angle: 60,
                            spread: 55,
                            origin: { x: 0 },
                            colors: ['#ff0000', '#ffd700', '#ff69b4', '#00ff00']
                        });
                        confetti({
                            particleCount: 8,
                            angle: 120,
                            spread: 55,
                            origin: { x: 1 },
                            colors: ['#ff0000', '#ffd700', '#ff69b4', '#00ff00']
                        });
                        if (Date.now() < end) {
                            requestAnimationFrame(frame);
                        }
                    }());
                </script>
            """
            components.html(confetti_and_clap_js, height=0, width=0)

            # 标记为已播放，防止刷新页面时无限放炮鼓掌
            st.session_state.just_completed = False

        st.header("🏆 恭喜通关！")

        supported_extensions = ['.jpg', '.jpeg', '.png']
        photo_to_show = None

        for ext in supported_extensions:
            temp_name = f"level_{st.session_state.current_level}{ext}"
            if os.path.exists(temp_name):
                photo_to_show = temp_name
                break 

        if photo_to_show:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(
                    photo_to_show, 
                    caption=f"🌟 恭喜可爱帅气聪明的吴伟骏打败了单元 {st.session_state.current_level} ！", 
                    use_container_width=True 
                )

        if 'level_start_time' in st.session_state:
            total_seconds = int(time.time() - st.session_state.level_start_time)
            m, s = divmod(total_seconds, 60)
            st.success(f"你成功消灭了单元 {st.session_state.current_level} 的所有错题，完全掌握了本单元的知识！\n\n⏱️ 本关总用时：**{m}分{s}秒**")
        else:
            st.success(f"你成功消灭了单元 {st.session_state.current_level} 的所有错题，完全掌握了本单元的知识！")

        if st.session_state.current_level == st.session_state.unlocked_level:
            if st.session_state.unlocked_level < 12:
                st.session_state.unlocked_level += 1
                st.info(f"🔓 成功解锁 **单元 {st.session_state.unlocked_level}**！")
            else:
                st.snow()
                st.warning("🎓 太强了！你已经解锁了所有的历史单元！")

        # 结算界面的按钮：左边回地图，右边冲向下一关
        col_back, col_action = st.columns(2)

        with col_back:
            if st.button("🏠 回到主页", use_container_width=True):
                st.session_state.current_level = None
                if 'level_start_time' in st.session_state:
                    del st.session_state['level_start_time']
                st.rerun()

        with col_action:
            next_level = st.session_state.current_level + 1
            if next_level <= 12:
                if st.button("🏃‍♂️ 冲向下一关！", use_container_width=True):
                    st.session_state.current_level = next_level
                    st.session_state.question_queue = list(quiz_data.get(next_level, []))
                    st.session_state.total_q_count = len(st.session_state.question_queue)
                    st.session_state.answered = False
                    st.session_state.level_start_time = time.time()
                    st.rerun()
