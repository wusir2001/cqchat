from PyQt5 import QtWidgets, QtCore
from . import MainGui


class MainPage(QtWidgets.QMainWindow, MainGui.Ui_MainWindow):
    """显示主页面
    """

    def __init__(self, data):
        super().__init__()
        self.setupUi(self)
        # 显示UI
        self.__data = data
        self.__init_data()
        self.__flash_init_Qt()
        self.__connect_event()
        self.__auto_refresh_ui()

    def __init_data(self):
        from .chat.chat_object import ChatObject
        self.ChatObject = ChatObject(self.__data)
        # 初始化ChatObject, 避免重复初始化
        self.current_contact = None

    def __connect_event(self):
        """绑定的信号槽
        """
        self.FriendTree.doubleClicked.connect(
            self.__doubleclick_FriendTree_item)  # 调取发送函数
        self.SendButton.setShortcut("Ctrl+Return")  # CTRL + 回车键绑定发送键
        self.SendButton.clicked.connect(self.__send_message)  # 调取发送函数

    def __flash_init_Qt(self):
        self.__init_FriendTree()

    def __init_FriendTree(self):
        friend_list = self.ChatObject.ChatList.FriendListObject()
        friend_info_list = friend_list.info.info()  # 好友信息
        if friend_info_list:
            #  self.__data.ui_data.widget.friend_tree.clear()
            self.FriendTree.clear()  # 清空联系人列表
            for i in friend_info_list:
                tree_widget = self.FriendTree
                self.load_contact_tree(tree_widget, i['category'], i)

    def __auto_refresh_ui(self):
        """定时刷新数据
        """
        self.refresh_MessageList_timer = QtCore.QTimer(self)
        self.refresh_MessageList_timer.timeout.connect(self.__load_MessageList)
        self.refresh_MessageList_timer.start(100)

    def __load_MessageList(self):
        """载入消息列表
        """

        def format_chat_record(chat_record_dict):
            """格式化消息信息
            """
            import time
            sender_name = chat_record_dict['sender_name']
            message_unit_time = chat_record_dict['message_unit_time']
            message_content = chat_record_dict['message_content']
            message_time = time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(message_unit_time))
            message = message_time + '|' + \
                "{:<{x}}".format(sender_name, x=20) + message_content
            return message

        current_contact = self.current_contact
        if current_contact is None:
            return False
        chat_record = current_contact.get_chat_record()
        root = self.MessageList
        root_count = root.count()
        for i in range(root_count, len(chat_record)):
            #  message_content = chat_record[i]['message_content']
            message_content = format_chat_record(chat_record[i])
            new_message = QtWidgets.QListWidgetItem()
            new_message.setText(message_content)
            self.MessageList.addItem(new_message)
            self.MessageList.scrollToBottom()

    def __doubleclick_FriendTree_item(self):
        try:
            current_contact_id = int(str(
                self.FriendTree.currentItem()))  # 获取好友ID
            self.current_contact = self.ChatObject.ChatIndividual.FriendObject(
                current_contact_id)
        except ValueError:
            pass
        else:
            self.InputBox.setFocus()  # 文本框获得焦点

    def __send_message(self):
        send_text = self.InputBox.toPlainText()
        self.InputBox.clear()
        # 发送键按下后获取输入框文本并清空
        if not len(send_text):
            return False
        current_contact = self.current_contact
        if current_contact:
            current_contact.message.send_message(send_text)

    def load_contact_tree(self, tree_widget, category, friend_info_list):
        from .ui.widgets import ChatTreeWidgetItem
        try:
            friend_markname = friend_info_list['markname']
        except KeyError:
            friend_markname = None
        if not friend_markname:
            friend_markname = friend_info_list['name']
        #  root = self.FriendTree.invisibleRootItem()
        root = tree_widget.invisibleRootItem()
        root_count = root.childCount()
        root_category_text_list = [
            root.child(i).text(0) for i in range(root_count)
        ]
        friend_item = ChatTreeWidgetItem({
            'name': friend_markname,
            'id': friend_info_list['id']
        })
        friend_item.setFlags(QtCore.Qt.ItemIsSelectable
                             | QtCore.Qt.ItemIsUserCheckable
                             | QtCore.Qt.ItemIsEnabled)
        # 创建好友组件
        if category in root_category_text_list:
            category_widget = self.FriendTree.findItems(
                category, QtCore.Qt.MatchFixedString)[0]
        else:
            category_widget = QtWidgets.QTreeWidgetItem([category])
            self.FriendTree.addTopLevelItem(category_widget)
            category_widget.setFlags(QtCore.Qt.ItemIsSelectable
                                     | QtCore.Qt.ItemIsDragEnabled
                                     | QtCore.Qt.ItemIsUserCheckable
                                     | QtCore.Qt.ItemIsEnabled)
        category_widget.addChild(friend_item)
        # 添加好友组件


def main(data):
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MainPage(data)
    ui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main(None)
