import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/schedule_event.dart';

Map<String, int> dayToWeekday = {
  'Monday': 1,
  'Tuesday': 2,
  'Wednesday': 3,
  'Thursday': 4,
  'Friday': 5,
  'Saturday': 6,
  'Sunday': 7,
};

Future<List<ScheduleEvent>> loadScheduleEvents() async {
  final String jsonString = await rootBundle.loadString('/Users/saradeshmukh/Desktop/RUPlanner-1/frontend/lib/assets/schedules/schedule.json');
  final Map<String, dynamic> json = jsonDecode(jsonString);

  final now = DateTime.now();
  final weekStart = now.subtract(Duration(days: now.weekday - 1)); // start of current week

  List<ScheduleEvent> events = [];

  for (final course in json['courses']) {
    final title = course['title'];
    for (final mt in course['meeting_times']) {
      final day = dayToWeekday[mt['day']]!;
      final startMin = mt['range'][0];
      final endMin = mt['range'][1];
      final building = mt['building'];

      final baseDay = weekStart.add(Duration(days: day - 1));
      final start = DateTime(baseDay.year, baseDay.month, baseDay.day, startMin ~/ 60, startMin % 60);
      final end = DateTime(baseDay.year, baseDay.month, baseDay.day, endMin ~/ 60, endMin % 60);

      events.add(ScheduleEvent(
        title: title,
        start: start,
        end: end,
        location: building,
      ));
    }
  }

  return events;
}
