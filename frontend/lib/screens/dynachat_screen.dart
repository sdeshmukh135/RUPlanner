import 'package:flutter/material.dart';
import '/screens/models/schedule_event.dart';

class DynaChatScreen extends StatefulWidget {
  final List<ScheduleEvent> currentSchedule;
  final Function(List<ScheduleEvent>) onScheduleFinalized;

  const DynaChatScreen({
    super.key,
    required this.currentSchedule,
    required this.onScheduleFinalized,
  });

  @override
  State<DynaChatScreen> createState() => _DynaChatScreenState();
}

class _DynaChatScreenState extends State<DynaChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<String> _chatHistory = [];
  List<ScheduleEvent> _pendingSchedule = [];

  @override
  void initState() {
    super.initState();
    _pendingSchedule = List.from(widget.currentSchedule);
  }

  void _handleUserInput(String input) {
    setState(() {
      _chatHistory.add("You: $input");
    });

    final updatedSchedule = _parseCommand(input);
    if (updatedSchedule != null) {
      setState(() {
        _pendingSchedule = updatedSchedule;
        _chatHistory.add("AI: Got it, I've updated your schedule.");
      });
    } else {
      _chatHistory.add("AI: Sorry, I couldn't understand that.");
    }

    _controller.clear();
  }

  List<ScheduleEvent>? _parseCommand(String input) {
  final lower = input.toLowerCase();
  final weekdayMap = {
    'monday': 1,
    'tuesday': 2,
    'wednesday': 3,
    'thursday': 4,
    'friday': 5,
    'saturday': 6,
    'sunday': 7,
  };

  if (lower.startsWith("cancel")) {
    final parts = lower.split("cancel")[1].trim().split(" on ");
    if (parts.length == 2) {
      final course = parts[0].trim();
      final day = parts[1].trim();
      final int? weekday = weekdayMap[day];
      if (weekday != null) {
        final updated = _pendingSchedule.where((e) {
          return !(e.title.toLowerCase().contains(course) &&
                   e.start.weekday == weekday);
        }).toList();
        return updated;
      }
    }
  }

  if (lower.startsWith("add")) {
    final regex = RegExp(
      r'add (.+) on (\w+) from (\d+)(am|pm) to (\d+)(am|pm) at (.+)',
    );
    final match = regex.firstMatch(lower);
    if (match != null) {
      final title = match.group(1)!.trim(); // coffee
      final day = match.group(2)!; // friday
      final startHour = int.parse(match.group(3)!);
      final startMeridiem = match.group(4)!;
      final endHour = int.parse(match.group(5)!);
      final endMeridiem = match.group(6)!;
      final location = match.group(7)!.trim(); // Hidden Grounds

      final weekday = weekdayMap[day];
      if (weekday == null) return null;

      int convertHour(int hour, String meridiem) {
        if (meridiem == 'am') return hour % 12;
        return hour % 12 + 12;
      }

      final startH = convertHour(startHour, startMeridiem);
      final endH = convertHour(endHour, endMeridiem);

      final today = DateTime.now();
      final baseDay = today.subtract(Duration(days: today.weekday - weekday));
      final start = DateTime(baseDay.year, baseDay.month, baseDay.day, startH);
      final end = DateTime(baseDay.year, baseDay.month, baseDay.day, endH);

      final newEvent = ScheduleEvent(
        title: title,
        start: start,
        end: end,
        location: location,
      );

      return [..._pendingSchedule, newEvent];
    }
  }

  return null;
}


  void _finalizeSchedule() {
    widget.onScheduleFinalized(_pendingSchedule);
    Navigator.pop(context); // Return to schedule screen
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('DynaChat'),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.account_circle, color: Colors.black),
            onPressed: () {},
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.all(16),
              itemCount: _chatHistory.length,
              itemBuilder: (context, index) => Text(_chatHistory[index]),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Start a conversation...',
                      filled: true,
                      fillColor: Colors.grey[200],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send, color: Colors.green),
                  onPressed: () => _handleUserInput(_controller.text),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton(
              onPressed: _finalizeSchedule,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.black,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
              ),
              child: Text("Finalize Schedule"),
            ),
          ),
        ],
      ),
    );
  }
}
