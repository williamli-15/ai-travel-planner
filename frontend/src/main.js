
/* jshint esversion: 6 */

import { createApp } from 'vue';
import App from './App.vue';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

import Chat from 'vue3-beautiful-chat';
const app = createApp(App);

import BaiduMap from 'vue-baidu-map-3x';
app.use(BaiduMap, {ak: 'UDVb7LAK20XmdY1vwGzSGeFbM2Up7OTj'});

app.use(ElementPlus);
app.use(Chat);
app.mount('#app');
