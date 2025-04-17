import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:googleapis/calendar/v3.dart' as calendar;
import 'package:googleapis_auth/auth_io.dart';
import 'package:http/http.dart' as http;
import '/screens/models/schedule_event.dart';
import '/screens/utils/parse_schedule.dart';
import 'dynachat_screen.dart';

class SchedulesScreen extends StatefulWidget {
  const SchedulesScreen({super.key});

  @override
  State<SchedulesScreen> createState() => _SchedulesScreenState();
}

class _SchedulesScreenState extends State<SchedulesScreen> {
  Map<DateTime, List<ScheduleEvent>> _events = {};
  DateTime _focusedDay = DateTime.now();
  DateTime _selectedDay = DateTime.now();

  final _clientId = ClientId(
    "CLIENT-ID",
    "CLIENT-SECRET",
  );

  final _scopes = [calendar.CalendarApi.calendarScope];

  @override
  void initState() {
    super.initState();
    _loadAndSetSchedule();
  }

  Future<void> _loadAndSetSchedule() async {
    final allEvents = await loadScheduleEvents();
    setState(() {
      _events = _groupEventsByDay(allEvents);
    });
  }

  Map<DateTime, List<ScheduleEvent>> _groupEventsByDay(List<ScheduleEvent> events) {
    final Map<DateTime, List<ScheduleEvent>> eventMap = {};
    for (var event in events) {
      final key = DateTime(event.start.year, event.start.month, event.start.day);
      eventMap[key] = [...?eventMap[key], event];
    }
    return eventMap;
  }

  Future<void> syncToGoogleCalendar() async {
    final allEvents = _events.values.expand((e) => e).toList();

    await clientViaUserConsent(_clientId, _scopes, (url) {
      print("Please go to the following URL to grant access:");
      print(url);
    }).then((authClient) async {
      final cal = calendar.CalendarApi(authClient);

      for (var e in allEvents) {
        final gEvent = calendar.Event()
          ..summary = e.title
          ..location = e.location
          ..start = calendar.EventDateTime(dateTime: e.start, timeZone: "America/New_York")
          ..end = calendar.EventDateTime(dateTime: e.end, timeZone: "America/New_York");

        await cal.events.insert(gEvent, "primary");
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Events synced to Google Calendar")),
      );

      authClient.close();
    });
  }

  void _navigateToDynaChat() {
    final currentSchedule = _events.values.expand((e) => e).toList();
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => DynaChatScreen(
          currentSchedule: currentSchedule,
          onScheduleFinalized: (List<ScheduleEvent> updatedEvents) {
            setState(() {
              _events = _groupEventsByDay(updatedEvents);
            });
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final selectedEvents = _events[DateTime(_selectedDay.year, _selectedDay.month, _selectedDay.day)] ?? [];

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text("DynaSched", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            Text("Schedules", style: TextStyle(fontSize: 14, color: Colors.green)),
          ],
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.account_circle, size: 30, color: Colors.black),
            onPressed: () {},
          ),
        ],
      ),
      body: Column(
        children: [
          TableCalendar<ScheduleEvent>(
            firstDay: DateTime.utc(2024),
            lastDay: DateTime.utc(2026),
            focusedDay: _focusedDay,
            selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
            onDaySelected: (selected, focused) {
              setState(() {
                _selectedDay = selected;
                _focusedDay = focused;
              });
            },
            eventLoader: (day) {
              return _events[DateTime(day.year, day.month, day.day)] ?? [];
            },
            calendarStyle: CalendarStyle(
              todayDecoration: BoxDecoration(color: Colors.green, shape: BoxShape.circle),
              selectedDecoration: BoxDecoration(color: Colors.black, shape: BoxShape.circle),
            ),
          ),
          Expanded(
            child: ListView(
              children: selectedEvents.map((e) {
                return ListTile(
                  title: Text(e.title),
                  subtitle: Text('${e.start.hour}:${e.start.minute.toString().padLeft(2, '0')} - ${e.end.hour}:${e.end.minute.toString().padLeft(2, '0')}'),
                  trailing: Text(e.location),
                );
              }).toList(),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 10),
            child: ElevatedButton.icon(
              icon: Icon(Icons.chat),
              label: Text("Open DynaChat"),
              onPressed: _navigateToDynaChat,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[900],
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 16),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(bottom: 16.0),
            child: ElevatedButton.icon(
              icon: Icon(Icons.sync),
              label: Text("Sync to Google Calendar"),
              onPressed: syncToGoogleCalendar,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.black,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }
}


