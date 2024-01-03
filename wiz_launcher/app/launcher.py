import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget, \
    QComboBox, QAction, QPushButton, QTableWidget, QTableWidgetItem
from PySide2.QtGui import QColor, QPalette, QIcon
from PySide2.QtCore import Qt
import subprocess

class AppLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_list = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('WizLauncher')
        self.apply_dark_theme()
        self.create_menu_bar()

        # メインレイアウト
        main_layout = QHBoxLayout()

        # プロジェクトリストカラム
        self.project_list = QListWidget()
        self.project_list.setFixedWidth(200)
        self.project_list.setStyleSheet("""
                   QListWidget {
                       outline: 0;  /* アウトラインを無効化 */
                   }
                   QListWidget::item {
                       padding: 10px;  /* アイテムのパディング */
                       font-size: 16px;  /* フォントサイズ */
                       border: none;  /* 枠線を消す */
                   }
                   QListWidget::item:selected {
                       background-color: #3b5998;  /* 選択されたアイテムの背景色 */
                       color: #ffffff;
                       border: none;  /* 選択されたアイテムの枠線を消す */
                   }
               """)
        self.project_list.addItem('MobileGame')
        self.project_list.addItem('CutSceneA')
        # その他のプロジェクトを追加...
        self.project_list.currentItemChanged.connect(self.on_project_selected)
        main_layout.addWidget(self.project_list)

        # ツール情報カラム
        self.tool_area = QWidget()
        self.tool_layout = QVBoxLayout()
        self.tool_area.setObjectName("ToolArea")  # スタイルシート用のオブジェクト名を設定
        self.tool_label = QLabel('プロジェクトを選択してください。')
        self.tool_layout.addWidget(self.tool_label)
        self.tool_area.setLayout(self.tool_layout)
        self.tool_area.setFixedWidth(300)
        self.tool_area.setMinimumSize(300, 400)
        main_layout.addWidget(self.tool_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def on_project_selected(self, current, previous):
        project_name = current.text() if current else ''
        self.update_tool_info(project_name)

    def update_tool_info(self, project_name):
        # プロジェクトに応じたツールとバージョンの情報を辞書で管理
        project_tools = {
            'MobileGame': [('Maya', '2023'), ('Blender', '2.93'), ('Photoshop', '2021'), ('Houdini', '18.5')],
            'CutSceneA': [('Photoshop', '2021'), ('Houdini', '18.5')]
            # その他のプロジェクトに対応するツールを追加...
        }
        # 各ツールに対応するアイコンのパス（例）
        tool_icons = {
            'Maya': 'app/icons/maya-icon.png',
            'Blender': 'app/icons/blender-icon.png',
            'Photoshop': 'app/icons/photoshop-icon.png',
            'Houdini': 'app/icons/houdini-icon.png',
            'Substance Painter': 'path/to/substance_painter_icon.png'
        }

        # ツール情報を表示するためのテーブルを作成
        tools = project_tools.get(project_name, [])
        self.tool_table = QTableWidget()
        self.tool_table.setStyleSheet("""
                    QTableWidget {
                                            border: 1px solid #2b3e5b;  /* 境界線色 */

                        background-color: #191825;  /* テーブルの背景色 */
                        color: #e0e1dd;  /* テーブルのテキスト色 */
                        gridline-color: #3a3a3a;  /* グリッド線の色 */
                    }
                    QHeaderView::section {
                                            gridline-color: #3a3a3a;  /* グリッド線の色 */

                        background-color: #1a1f2b;  /* ヘッダーの背景色 */
                        padding: 5px;
                        border: 1px solid #3a3a3a;  /* ヘッダーの境界線 */
                                                color: #e0e1dd;  /* テーブルのテキスト色 */

                    }
                    QTableWidget::item:selected {
                        background-color: #3b5998;  /* 選択されたアイテムの背景色 */
                        color: #ffffff;
                    }
                """)

        self.tool_table.setColumnCount(2)  # 2列 (ツール名とバージョン)
        self.tool_table.setHorizontalHeaderLabels(['Name', 'Version'])
        self.tool_table.setRowCount(len(tools))

        # テーブルの選択モードと選択動作を設定
        self.tool_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tool_table.setSelectionMode(QTableWidget.SingleSelection)

        # ツール名、バージョン、およびアイコンをテーブルに追加
        for i, (tool_name, version) in enumerate(tools):
            icon_path = tool_icons.get(tool_name, '')  # アイコンのパスを取得
            if icon_path:
                icon = QIcon(icon_path)
                item = QTableWidgetItem(icon, tool_name)
            else:
                item = QTableWidgetItem(tool_name)
            self.tool_table.setItem(i, 0, item)
            self.tool_table.setItem(i, 1, QTableWidgetItem(version))

        self.tool_table.horizontalHeader().setStretchLastSection(True)
        self.tool_table.verticalHeader().setVisible(False)
        self.tool_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # ツール情報カラムの内容をクリアしてテーブルを追加
        self.clear_layout(self.tool_layout)
        self.tool_layout.addWidget(self.tool_table)

        # 起動ボタンを追加
        self.launch_button = QPushButton('Launch')
        self.launch_button.clicked.connect(self.launch_selected_tool)
        self.tool_layout.addWidget(self.launch_button)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def launch_selected_tool(self):
        # 選択されたツールに応じて異なる動作を実行
        current_tool = self.project_list.currentItem().text()
        # 例: if current_tool == 'Maya': subprocess.Popen([...])

    def apply_dark_theme(self):
        # スタイルシートの定義
        styleSheet = """
                    QMainWindow, QWidget {
                        background-color: #2A2F4F;  /* 基本の背景色 */
                    }
                    QLabel, QPushButton, QListWidget, QComboBox {
                        color: #e0e1dd;  /* テキストの色 */
                        background-color: #191825;  /* 要素の背景色 */
                        border: 1px solid #2b3e5b;  /* 境界線色 */
                        border-radius: 2px;  /* 角を丸くする */
                    }
                    QPushButton:hover {
                        background-color: #000000;  /* ボタンホバー時の青色 */
                    }
                    QPushButton:pressed {
                        background-color: #2b3e5b;  /* ボタン押下時の濃い青色 */
                    }
                    QMenuBar, QMenu {
                        background-color: #191825;
                        color: #e0e1dd;
                    }
                    QMenuBar::item:selected, QMenu::item:selected {
                        background-color: #3b5998;
                    }
                    QListWidget::item:selected, QComboBox::drop-down {
                        background-color: #191825;
                        color: #e0e1dd;
                    }
                    #ToolArea {
                        border: 1px solid #2b3e5b;  /* 境界線色 */

                        background-color: #191825;  /* 要素の背景色 */
                        border-radius: 2px;  /* 角を丸くする */
                    }
                """

        # スタイルシートの適用
        self.setStyleSheet(styleSheet)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # ファイルメニュー
        file_menu = menu_bar.addMenu('&File')
        project_menu = menu_bar.addMenu('&Project')
        setting_menu = menu_bar.addMenu('&Settings')
        help_menu = menu_bar.addMenu('&Help')

        # ファイルメニュー内のアクション
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def on_app_selected(self, current, previous):
        app_name = current.text() if current else ''
        self.detail_label.setText(f'{app_name}の情報:')
        self.update_version_selector(app_name)

    def update_version_selector(self, app_name):
        self.version_selector.clear()
        versions = {
            'Maya': ['2023', '2022', '2021', '2020'],
            'Blender': ['2.93', '2.92', '2.91'],
            'Photoshop': ['2021', '2020', '2019'],
            'Houdini': ['18.5', '18.0', '17.5'],
            'Substance Painter': ['7.2', '7.1', '7.0']
        }
        self.version_selector.addItems(versions.get(app_name, []))

    def launch_maya(self, version):
        maya_path = f"C:\\Program Files\\Autodesk\\Maya{version}\\bin\\maya.exe"
        subprocess.Popen([maya_path])

    def launch_selected_app(self):
        selected_app = self.app_list.currentItem()
        selected_version = self.version_selector.currentText()
        if selected_app and selected_version:
            if selected_app.text() == 'Maya':
                self.launch_maya(selected_version)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppLauncher()
    ex.show()
    sys.exit(app.exec_())
