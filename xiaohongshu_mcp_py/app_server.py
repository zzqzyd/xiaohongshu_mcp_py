from flask import Flask, request, jsonify
from loguru import logger
import threading
import time


class AppServer:
    def __init__(self, xiaohongshu_service):
        self.app = Flask(__name__)
        self.service = xiaohongshu_service
        self.server_thread = None
        self.stop_event = threading.Event()
        
        # 注册路由
        self._register_routes()
    
    def _register_routes(self):
        # 健康检查
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'ok'}), 200
        
        # API v1 路由组
        @self.app.route('/api/v1/check_login', methods=['GET'])
        def check_login():
            try:
                status = self.service.check_login_status()
                return jsonify({'success': True, 'data': status}), 200
            except Exception as e:
                logger.error(f"检查登录状态失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/v1/publish', methods=['POST'])
        def publish():
            try:
                data = request.json
                if not data:
                    return jsonify({'success': False, 'message': '未提供数据'}), 400
                
                result = self.service.publish_content(data)
                return jsonify({'success': True, 'data': result}), 200
            except Exception as e:
                logger.error(f"发布失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/v1/feeds', methods=['GET'])
        def get_feeds():
            try:
                page = request.args.get('page', 1, type=int)
                size = request.args.get('size', 20, type=int)
                
                feeds = self.service.get_feeds(page, size)
                return jsonify({'success': True, 'data': feeds}), 200
            except Exception as e:
                logger.error(f"获取推荐列表失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/v1/search', methods=['GET'])
        def search():
            try:
                keyword = request.args.get('keyword', '')
                page = request.args.get('page', 1, type=int)
                size = request.args.get('size', 20, type=int)
                
                if not keyword:
                    return jsonify({'success': False, 'message': '请输入搜索关键词'}), 400
                
                results = self.service.search_content(keyword, page, size)
                return jsonify({'success': True, 'data': results}), 200
            except Exception as e:
                logger.error(f"搜索失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/v1/note_detail', methods=['GET'])
        def get_note_detail():
            try:
                note_id = request.args.get('note_id', '')
                
                if not note_id:
                    return jsonify({'success': False, 'message': '请输入笔记ID'}), 400
                
                detail = self.service.get_note_detail(note_id)
                return jsonify({'success': True, 'data': detail}), 200
            except Exception as e:
                logger.error(f"获取笔记详情失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500
        
        @self.app.route('/api/v1/comment', methods=['POST'])
        def comment():
            try:
                data = request.json
                if not data or 'note_id' not in data or 'content' not in data:
                    return jsonify({'success': False, 'message': '缺少必要的字段'}), 400
                
                result = self.service.post_comment(data['note_id'], data['content'])
                return jsonify({'success': True, 'data': result}), 200
            except Exception as e:
                logger.error(f"发表评论失败: {str(e)}")
                return jsonify({'success': False, 'message': str(e)}), 500
    
    def start(self, host='0.0.0.0', port=18060):
        """启动服务器"""
        def run_server():
            try:
                self.app.run(host=host, port=port, threaded=True, debug=False)
            except Exception as e:
                if not self.stop_event.is_set():
                    logger.error(f"Server error: {str(e)}")
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # 保持主线程运行
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止服务器"""
        logger.info("Stopping server...")
        self.stop_event.set()
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)