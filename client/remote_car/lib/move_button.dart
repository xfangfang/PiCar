import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

class MoveButton extends StatefulWidget {
  Function updateListener;
  double innerRadius;
  double outterRadius;
  bool autoback;

  MoveButton({Key key, this.updateListener, this.outterRadius=70, this.innerRadius=20, this.autoback=true})
      : super(key: key);
  @override
  _MoveButtonState createState() => _MoveButtonState();
}

class _MoveButtonState extends State<MoveButton> {
  double _initCenter = 50;
  double _long = 100;
  double _short = 0;

  double _left = 50;
  double _top = 50;

  Function onUpdate;

  @override
  void initState() {
    super.initState();
    if(widget.updateListener != null){
      this.onUpdate = widget.updateListener;
    }
    
    
    setState(() {
      _initCenter = widget.outterRadius - widget.innerRadius ;
      _long = _initCenter * 2;
      _top = _initCenter;
      _left = _initCenter;
    });
    
  }

  void _onDown(DragDownDetails e){
    print("用户手指按下：${e.globalPosition}");
  }

  void _onUpdate(DragUpdateDetails e){
    setState(() {
      _left += e.delta.dx;
      if(_left > _long){
        _left = _long;
      }else if(_left < _short){
        _left = _short;
      }
      _top += e.delta.dy;
      if(_top > _long){
        _top = _long;
      }else if(_top < _short){
        _top = _short;
      }
    });

    if(this.onUpdate != null){
      this.onUpdate(_left*100/_long, (_long-_top)*100/_long);
    }

  }

  

  void _onEnd(DragEndDetails e){
    print(e.velocity);
    _initCenter = widget.outterRadius - widget.innerRadius;

    if(widget.autoback){
      setState(() {
        _left = _initCenter;
        _top = _initCenter;
      });
    }
    
    if(this.onUpdate != null){
      this.onUpdate(0.0,0.0);
    }
  }

  


  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: BoxConstraints.expand(width: widget.outterRadius*2,height: widget.outterRadius*2),
      child: Stack(children: <Widget>[
        Positioned(
          top: 0,
          left: 0,
          child: CircleAvatar(
            backgroundColor: Color(0x88888888),
            radius: widget.outterRadius,
          ),
        ),
        Positioned(
          top: _top,
          left: _left,
          child: GestureDetector(
            child:CircleAvatar(
              backgroundColor: Color(0xFF888888),
              radius: widget.innerRadius,
            ),
            onPanDown: _onDown,
            onPanUpdate: _onUpdate,
            onPanEnd: _onEnd,
          )
        )
      ],
    ));
  }
}
