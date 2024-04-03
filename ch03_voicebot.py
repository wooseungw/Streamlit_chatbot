import streamlit as st
# audiorecorder 패키지 추가
from audiorecorder import audiorecorder

# OpenAI 패키지 추가
import openai
# 파일 삭제를 위한 패키지 추가
import os
# 시간 정보를 위한 패키지 추가
from datetime import datetime

# TTS 패키지 추가
# from gtts import gTTS

# 음원 파일을 재생하기 위한 패키지 추가
# import base64

##### 기능 구현 함수 #####
def STT(audio, apikey):          
       # 파일 저장
       filename='input.mp3'
       audio.export(filename, format="mp3")

       # 음원 파일 열기
       audio_file = open(filename, "rb")
       # Whisper 모델을 활용해 텍스트 얻기
       client = openai.OpenAI(api_key = apikey)
       response = client.audio.transcriptions.create(model = "whisper-1", file = audio_file)
       audio_file.close()
       # 파일 삭제
       os.remove(filename)
       return response.text

def ask_gpt(prompt, model, apikey):                 ################################################################# p.49 참고하여 수정
       client = openai.OpenAI(api_key = apikey)
       response = client.chat.completions.create(
             model=model,
             messages=prompt,                              # 온도(temperature)는 [0,2]의 범위를 갖지만, 2로 설정할 경우 알아듣기 힘든 수준이라 1.4로 설정했습니다.
             temperature=1.4,      # 추가                  # 존재 패널티(presence_penalty)는 [0,2]의 범위를 갖고, 2로 설정하여 새로운 주제에 대한 이야기 가능성↑
             presence_penalty=2,   # 추가                  # 빈도수 패널티(frequency_penalty)는 [0,2]의 범위를 갖고, 2로 설정하여 특정 단어의 반복을 줄임
             frequency_penalty=2)  # 추가                          
       gptResponse = response.choices[0].message.content   # 핵 샘플링(top_p) 또한 자유분방한 문장을 생성하는데에 영향을 미치지만,
       return gptResponse                                  # 설정값의 범위가 [0,1] 이고, 값을 설정하지 않으면 1로 설정되기 때문에 별도의 코드를 추가하지 않았습니다.

# def TTS(response):
    # gTTS 를 활용하여 음성 파일 생성
#    filename = "output.mp3"
#    tts = gTTS(text=response,lang="ko")
#    tts.save(filename)

    # 음원 파일 자동 재생
#    with open(filename, "rb") as f:
#        data = f.read()
#        b64 = base64.b64encode(data).decode()
#        md = f"""
#            <audio autoplay="True">
#            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
#            </audio>
#            """
#        st.markdown(md,unsafe_allow_html=True,)
#    # 파일 삭제
#    os.remove(filename)

       
##### 메인 함수 #####
def main():
        # 기본 설정
        st.set_page_config(
            page_title="음성 비서 프로그램",
            layout="wide")
        
        # session state 초기화 - p.85 (뒤에서 추가함)
        if "chat" not in st.session_state:
               st.session_state["chat"] = []
        
        if "OPENAI_API" not in st.session_state:
               st.session_state["OPENAI_API"] = ""
        
        if "messages" not in st.session_state:
               st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
        
        if "check_reset" not in st.session_state:
               st.session_state["check_reset"] = False
  
        # 제목
        st.header("개성 넘치는 음성 비서 프로그램")

        # 구분선
        st.markdown("---")

        # 기본 설명
        with st.expander("개성 넘치는 음성비서 프로그램 사용법", expanded=True):
                st.write(
                """
                - 지루하고 딱딱한 챗봇은 그만! 개성 넘치는 대화를 나눠보세요.
                - 음성으로 질문하거나 텍스트를 입력하여 대화할 수 있어요.
                - 친구와 대화하듯 편하게 질문해 보세요.
                - 친구가 대답하듯 개성있고 재미있는 답변을 들을 수 있을 거에요.
                """

                )

                st.markdown("")

        # 사이드바 생성           
        with st.sidebar:
                
                # Open AI API 키 입력받기
                st.session_state["OPENAI_API"] = st.text_input(label="OPENAI API 키", placeholder="Enter Your API Key", value="", type="password")

                st.markdown("")

                # GPT 모델을 선택하기 위한 라디오 버튼 생성
                model = st.radio(label="GPT 모델", options=["gpt-3.5-turbo", "gpt-4"])

                st.markdown("---")

                # 리셋 버튼 생성                    
                if st.button(label="초기화"):
                    # 리셋 코드 - 처음에는 if문 뒤에 아무것도 없어서 오류가 났으나, p.85에 session 함수에 대한 설명이 후술됨.
                     st.session_state["chat"] = []
                     st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
                     st.session_state["check_reset"] = True
                     
        # 기능 구현 공간
        col1, col2 = st.columns(2)
        with col1:
               # 왼쪽 영역 작성          
               st.subheader("질문하기🎙️/⌨️")
               # 음성 녹음 아이콘 추가
               audio = audiorecorder("음성 질문🎙️", "듣고 있어요...👂")

               if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
               # 녹음을 실행하면?
                      # 음성 재생
                      st.audio(audio.export().read())
                      # 음원 파일에서 텍스트 추출
                      question = STT(audio, st.session_state["OPENAI_API"])
                     
                      # 채팅을 시각화하기 위해 질문 내용 저장
                      now = datetime.now().strftime("%H:%M")
                      st.session_state["chat"] = st.session_state["chat"]+ [("user",now, question)]

                      # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
                      st.session_state["messages"] = st.session_state["messages"]+ [{"role": "user", "content": question}]

               # 텍스트 입력 위젯 추가
               text_question = st.text_input(label="아래에 텍스트를 입력하세요 👇", key="text_input")

               if st.button("텍스트 질문⌨️") and text_question and (st.session_state["check_reset"] == False):
                      # 텍스트 질문 버튼을 클릭한 경우

                      # 채팅을 시각화하기 위해 질문 내용 저장
                      now = datetime.now().strftime("%H:%M")
                      st.session_state["chat"] = st.session_state["chat"]+ [("user",now, text_question)]

                      # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
                      st.session_state["messages"] = st.session_state["messages"]+ [{"role": "user", "content": text_question}]
               
           
        with col2:
               # 오른쪽 영역 작성
               st.subheader("질문/답변")
               if  (audio.duration_seconds > 0 or text_question) and (st.session_state["check_reset"]==False):
                   # ChatGPT에게 답변 얻기
                   response = ask_gpt(st.session_state["messages"], model, st.session_state["OPENAI_API"])

                   # GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
                   st.session_state["messages"] = st.session_state["messages"]+ [{"role": "system", "content": response}]

                   # 채팅 시각화를 위한 답변 내용 저장
                   now = datetime.now().strftime("%H:%M")
                   st.session_state["chat"] = st.session_state["chat"]+ [("bot",now, response)]

               # 채팅 형식으로 시각화 하기       
               for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")              
              
                # gTTS를 활용하여 음성 파일 생성 및 재생
                #    TTS(response)
                                   

if __name__=="__main__":
    main()
    