<template>
  <div id="app">
    <ChatComponent></ChatComponent>
  </div>
</template>

<script>
import ChatComponent from './components/ChatComponent.vue'

export default {
  name: 'App',
  components: {
    ChatComponent
  }
}
</script>

<style>
#app {
  height: 100%;
  width: 100%;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
