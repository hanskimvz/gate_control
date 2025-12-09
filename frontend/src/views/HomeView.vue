<template>
  <div class="home-view">
    <div class="container">
      <h1>Gate Control System</h1>
      <p>문 제어 시스템에 오신 것을 환영합니다.</p>
      
      <div class="links">
        <router-link to="/gate" class="link-card">
          <h2>문 열기</h2>
          <p>카메라 스냅샷을 확인하고 문을 열 수 있습니다.</p>
        </router-link>
        
        <router-link to="/logs" class="link-card">
          <h2>로그 조회</h2>
          <p>문 열기 이벤트 로그를 확인할 수 있습니다.</p>
        </router-link>
        
        <router-link to="/users" class="link-card">
          <h2>사용자 관리</h2>
          <p>사용자 정보를 관리할 수 있습니다.</p>
        </router-link>
      </div>
      
      <div class="info">
        <p><strong>사용 방법:</strong></p>
        <p>각 페이지에 접근하려면 URL에 <code>?api_key=YOUR_API_KEY</code>를 추가하세요.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home-view {
  width: 100%;
  min-height: 100%;
  background-color: #f5f5f5;
  padding: 40px 20px;
  box-sizing: border-box;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 10px;
}

.container > p {
  text-align: center;
  color: #666;
  margin-bottom: 40px;
}

.links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.link-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 8px;
  text-decoration: none;
  transition: transform 0.3s, box-shadow 0.3s;
}

.link-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
}

.link-card h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.link-card p {
  margin: 0;
  opacity: 0.9;
}

.info {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 4px;
  border-left: 4px solid #3498db;
}

.info p {
  margin: 10px 0;
  color: #333;
}

.info code {
  background-color: #e8e8e8;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}
</style>
