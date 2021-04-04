import 'dart:async';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:webview_flutter/webview_flutter.dart';

import 'move_button.dart';

const HOST = '192.168.123.20:6082';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  SystemChrome.setPreferredOrientations(
      [DeviceOrientation.landscapeLeft, DeviceOrientation.landscapeRight]);

  SystemChrome.setEnabledSystemUIOverlays([]);

  runApp(MyApp());
}

class WebSocket {
  WebSocketChannel _webSocket;
  var onMessage;
  var onDone;
  var send;

  void initWebSocket(onMessage, onDone, send) {
    this.onMessage = onMessage;
    this.onDone = onDone;
    this.send = send;
    var path = 'ws://' + HOST + '/ws';
    _webSocket = IOWebSocketChannel.connect(path);
    _webSocket.stream.listen(this.onMessage, onDone: this.onDone);
  }

  void close() {
    _webSocket.sink.close(status.goingAway);
  }
}

class MyApp extends StatelessWidget {
  // This widget is the root of your application.

  @override
  Widget build(BuildContext context) {
    final title = "remote Car";
    final websocket = WebSocket();
    return MaterialApp(
        title: title,
        theme: ThemeData(primarySwatch: Colors.green),
        home: MyHomePage(title: title, websocket: websocket));
  }
}

class MyHomePage extends StatefulWidget {
  final String title;
  final WebSocket websocket;

  MyHomePage({Key key, @required this.title, @required this.websocket})
      : super(key: key);

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  var sendTime = DateTime.now().millisecondsSinceEpoch;
  var upClick = false;
  var downClick = false;
  var leftClick = false;
  var rightClick = false;
  var delay = "";
  static WebViewController _controller;
  // "https://www.baidu.com",//
  var webview = WebView(
      initialUrl: "http://" + HOST,
      javascriptMode: JavascriptMode.unrestricted,
      onWebViewCreated: (WebViewController webViewController) {
        _controller = webViewController;
      });

  // _MyHomePageState(){
  //   initWebsocket();
  // }

  @override
  void initState() {
    super.initState();
    initWebsocket();
  }

  void initWebsocket() {
    widget.websocket.initWebSocket(onMessage, onDone, send);
  }

  void send(message) {
    if (widget.websocket._webSocket == null) {
      print('init new websocket');
      initWebsocket();
    } else {
      widget.websocket._webSocket.sink.add(message);
    }
  }

  void sendTest() {
    if (widget.websocket._webSocket.closeCode == null) {
      _test();
      Future.delayed(Duration(seconds: 1), () {
        sendTest();
      });
    }
  }

  void onDone() {
    print("ws closed");
    setState(() {
      delay = '已断开连接';
    });
    Future.delayed(Duration(seconds: 1), () {
      print('延时1s启动新的websocket');
      initWebsocket();
    });
  }

  void onMessage(message) {
    print("message: " + message);

    if (message == 'test') {
      updateDelay();
    } else if (message == 'START') {
      sendTest();
    }
  }

  void _test() {
    print('测试延时');
    sendTime = DateTime.now().millisecondsSinceEpoch;
    send('test');
  }

  void refreshWebview() {
    // print(window.physicalSize.height);
    // print(window.devicePixelRatio);
    if (_controller != null) {
      _controller.reload();
    }
  }

  Future<bool> showDeleteConfirmDialog1() {
    return showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text("提示"),
          content: Text("收到ws服务器发来的消息"),
          actions: <Widget>[
            FlatButton(
              child: Text("取消"),
              onPressed: () => Navigator.of(context).pop(),
            ),
            FlatButton(
              child: Text("确定"),
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    widget.websocket.close();
    super.dispose();
  }

  void updateDelay() {
    var difference = DateTime.now().millisecondsSinceEpoch - sendTime;
    // return Text(snapshot.hasData ? '延时 $difference ms' : '');

    setState(() {
      delay = '延迟' + '$difference' + 'ms';
    });
  }

  void _up(tapDown) {
    if (downClick) return;
    if (tapDown) {
      send('up-down');
      upClick = true;
    } else {
      send('up-up');
      upClick = false;
    }
  }

  void _down(tapDown) {
    if (upClick) return;
    if (tapDown) {
      send('down-down');
      downClick = true;
    } else {
      send('down-up');
      downClick = false;
    }
  }

  void _left(tapDown) {
    if (rightClick) return;
    if (tapDown) {
      send('left-down');
      leftClick = true;
    } else {
      send('left-up');
      leftClick = false;
    }
  }

  void _right(tapDown) {
    if (leftClick) return;
    if (tapDown) {
      send('right-down');
      rightClick = true;
    } else {
      send('right-up');
      rightClick = false;
    }
  }

  void _servoUpdateListener(double a, double b) {
    print("s" + '$a' + "-" + "$b");
    send('s-' + '$a' + '-' + '$b');
  }

  void _motorUpdateListener(double a, double b) {
    print("m" + '$a' + "-" + "$b");
    send('m-' + '$a' + '-' + '$b');
  }

  @override
  Widget build(BuildContext context) {
    double windowWidth = window.physicalSize.width / window.devicePixelRatio;
    double windowHeight = window.physicalSize.height / window.devicePixelRatio;
    double minWidth = windowHeight < windowWidth ? windowHeight : windowWidth;

    return Scaffold(
        // appBar: AppBar(
        //   // Here we take the value from the MyHomePage object that was created by
        //   // the App.build method, and use it to set our appbar title.
        //   title: Text(widget.title),
        // ),
        // drawer: Text("haha"),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
        floatingActionButton: FloatingActionButton(
            onPressed: refreshWebview,
            tooltip: '刷新视频',
            child: Icon(Icons.refresh)),
        body: ConstrainedBox(
          constraints: BoxConstraints.expand(),
          child: Stack(alignment: Alignment.center, children: <Widget>[
            //background
            Positioned(
              child: Container(
                  decoration: BoxDecoration(
                gradient: LinearGradient(colors: [
                  Color(0xff000000),
                  Color(0xff232323),
                  Color(0xff000000),
                ], begin: Alignment.centerLeft, end: Alignment.centerRight),
              )),
            ),
            // webview
            Container(
              height: windowHeight < windowWidth
                  ? windowHeight
                  : windowWidth * 3 / 4,
              width: windowWidth < windowHeight
                  ? windowWidth
                  : windowHeight * 4 / 3,
              child: webview,
            ),
            //Text
            Positioned(
              top: 0,
              left: 20,
              child: Text(
                delay,
                style: TextStyle(
                  color: Color(0x88888888),
                  fontSize: 18.0,
                ),
              ),
            ),
            Positioned(
                left: 50,
                bottom: 50,
                child: MoveButton(
                  updateListener: _motorUpdateListener,
                  innerRadius: minWidth / 15,
                  outterRadius: minWidth / 4,
                )),
            Positioned(
                right: 50,
                bottom: 50,
                child: MoveButton(
                  updateListener: _servoUpdateListener,
                  innerRadius: minWidth / 15,
                  outterRadius: minWidth / 4,
                  autoback: false,
                )),
            // direction buttons
            // Positioned(
            //   right: 0,
            //   child: Column(
            //     mainAxisAlignment: MainAxisAlignment.center,
            //     children: <Widget>[

            //       Column(mainAxisAlignment: MainAxisAlignment.center,
            //       children: <Widget>[
            //           Padding(
            //               padding: const EdgeInsets.fromLTRB(10.0, 10.0, 10.0, 10.0),
            //               child: RaisedButton(
            //                 onPressed: () {},
            //                 onHighlightChanged: _up,
            //                 child: Container(
            //                   height: 80,
            //                   width: 20,
            //                   alignment: Alignment.center,
            //                   child: Text('上'),
            //                 ),
            //               )),
            //           Row(
            //             mainAxisAlignment: MainAxisAlignment.center,
            //             children: <Widget>[
            //               Padding(
            //                   padding:
            //                       const EdgeInsets.fromLTRB(10.0, 10.0, 30.0, 10.0),
            //                   child: RaisedButton(
            //                     onPressed: () {},
            //                     onHighlightChanged: _left,
            //                     child: Container(
            //                       height: 80,
            //                       width: 20,
            //                       alignment: Alignment.center,
            //                       child: Text('左'),
            //                     ),
            //                   )),
            //               Padding(
            //                   padding:
            //                       const EdgeInsets.fromLTRB(30.0, 10.0, 10.0, 10.0),
            //                   child: RaisedButton(
            //                     onPressed: () {},
            //                     onHighlightChanged: _right,
            //                     child: Container(
            //                       height: 80,
            //                       width: 20,
            //                       alignment: Alignment.center,
            //                       child: Text('右'),
            //                     ),
            //                   )),
            //             ],
            //           ),
            //           Padding(
            //             padding: const EdgeInsets.fromLTRB(10.0, 10.0, 10.0, 10.0),
            //             child: RaisedButton(
            //               onPressed: () {},
            //               onHighlightChanged: _down,
            //               child: Container(
            //                 height: 80,
            //                 width: 20,
            //                 alignment: Alignment.center,
            //                 child: Text('下'),
            //               ),
            //             )),
            //         ]),],),
            // )
          ]),
        ));
  }
}
