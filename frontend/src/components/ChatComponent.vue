<template>
  <div>
    <beautiful-chat
        :participants="participants"
        :titleImageUrl="titleImageUrl"
        :onMessageWasSent="onMessageWasSent"
        :messageList="messageList"
        :newMessagesCount="newMessagesCount"
        :isOpen="isChatOpen"
        :close="closeChat"
        :open="openChat"
        :showEmoji="false"
        :showFile="false"
        :showEdition="false"
        :showDeletion="false"
        :showTypingIndicator="showTypingIndicator"
        :showLauncher="false"
        :showCloseButton="false"
        :colors="colors"
        :title="title"
        :alwaysScrollToBottom="alwaysScrollToBottom"
        :disableUserListToggle="true"
        :messageStyling="messageStyling"
        @onType="handleOnType"
        @edit="editMessage"
    />
    <div class="detect-list">
      <div class="detect-title">
        推荐
      </div>
      <el-tag v-if="detectAddressList.length===0">暂无 | 请输入您的目的地</el-tag>
      <el-tag class="recommend-item" v-else v-for="address in detectAddressList" :key="address" @click="clickAddress">
        {{ address }}
      </el-tag>
    </div>
    <div id="map-container" class="custom-map"></div>
  </div>
</template>

<script>

import axios from 'axios';
import AMapLoader from '@amap/amap-jsapi-loader';
import {shallowRef} from '@vue/reactivity';

window._AMapSecurityConfig = {
  securityJsCode: 'e626eae44037d1fdb59d81b5fb4bf15b'
}

export default {
  name: "ChatComponent",
  setup() {
    const map = shallowRef(null);
    return {
      map,
    }
  },
  data() {
    return {
      AMap: null,
      title: "智能行程规划",
      participants: [
        {
          id: 'me',
          name: 'me',
        },
        {
          id: 'robot',
          name: 'robot',
        }
      ],
      // titleImageUrl: 'https://avatars.githubusercontent.com/u/16464663?s=40&v=4',
      messageList: [
        {type: 'text', author: `robot`, data: {text: `您好，我是智能行程助手，输入：我想去香港。可以帮您智能规划行程噢~`}},
      ],
      newMessagesCount: 0,
      isChatOpen: true,
      showTypingIndicator: '',
      colors: {
        header: {
          bg: '#4e8cff',
          text: '#ffffff'
        },
        launcher: {
          bg: '#4e8cff'
        },
        messageList: {
          bg: '#ffffff'
        },
        sentMessage: {
          bg: '#4e8cff',
          text: '#ffffff'
        },
        receivedMessage: {
          bg: '#eaeaea',
          text: '#222222'
        },
        userInput: {
          bg: '#f4f7f9',
          text: '#565867'
        }
      },
      alwaysScrollToBottom: false,
      messageStyling: true,

      // map
      detectAddressList: [],
    }
  },
  methods: {
    initMap() {
      AMapLoader.load({
        key: "3c6e5e356fc76ddf66dfbdee26c4420a",
        version: "2.0",
        plugins: ['AMap.Geocoder', 'AMap.Geolocation'],
      }).then((AMap) => {
        this.AMap = AMap
        this.map = new AMap.Map("map-container", {
          zoom: 15,
          center: [105.602725, 37.076636],
          resizeEnable: true,
          viewMode: '3D',
        });
      }).catch(e => {
        console.log(e);
      })
    },
    sendMessage(text) {
      if (text.length > 0) {
        axios
            .post('http://127.0.0.1:5000/api/query', {
              query: text,
            })
            .then(response => {
              const respMsg = response.data.message
              const messageObj = {
                author: 'robot',
                type: 'text',
                data: {
                  text: respMsg,
                }
              }
              this.detectAddressList = []
              const tags = response.data.tags
              for (let i = 0; i < tags.length; i++) {
                let tag = tags[i];
                if (this.detectAddressList.indexOf(tag) !== -1) {
                  continue
                }
                this.detectAddressList.push(tag)
              }
              if (respMsg !== null && respMsg.length > 0) {
                this.messageList = [...this.messageList, messageObj]
              }
            })
            .catch(error => {
              console.error('POST请求失败:', error);
            });
      }
    },
    onMessageWasSent(message) {
      this.messageList = [...this.messageList, message]
      this.sendMessage(message.data.text)
    },
    openChat() {
      this.isChatOpen = true
      this.newMessagesCount = 0
    },
    closeChat() {
      this.isChatOpen = false
    },
    handleOnType() {

    },
    editMessage(message) {
      const m = this.messageList.find(m => m.id === message.id)
      m.isEdited = true
      m.data.text = message.data.text
    },
    searchLocation(address) {
      // 使用地理编码服务进行搜索
      this.AMap.plugin('AMap.Geocoder', () => {
        const geocoder = new this.AMap.Geocoder({});
        geocoder.getLocation(address, (status, result) => {
          console.info(status, result)
          if (status === 'complete' && result.geocodes.length > 0) {
            const location = result.geocodes[0].location;
            this.map.setCenter(location);
          } else {
            alert('地名搜索失败，请检查输入的地名。');
          }
        });
      });
    },
    clickAddress(e) {
      const text = e.target.innerText
      this.searchLocation(text)
    },
  },
  mounted() {
    this.initMap();
  }
}
</script>

<style scoped>

>>> div.sc-chat-window {
  position: fixed;

  width: 370px;
  max-height: 800px;
  left: 50px;
  bottom: 100px;
  height: 800px;
  box-sizing: border-box;
  box-shadow: 0px 7px 40px 2px rgba(148, 149, 150, 0.1);
  background: white;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 10px;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  animation: fadeIn;
  animation-duration: 0.3s;
  animation-timing-function: ease-in-out;
}

.detect-list {
  position: fixed;
  max-width: 200px;
  top: 100px;
  left: 600px;

  height: 800px;
}

.detect-title {
  margin-bottom: 10px;
  font-size: 30px;
  font-weight: bold;
}

.recommend-item {
  margin: 3px 2px 3px 1px;
}

.custom-map {
  position: fixed;
  max-height: 1000px;
  left: 950px;
  bottom: 100px;
  /**/
  width: 700px;
  height: 800px;

  border-radius: 10px; /* 圆角边框半径 */
  border: 2px solid #ccc; /* 边框样式 */
}

</style>