import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Text(
          'DynaSched',
          style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 28),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.account_circle, color: Colors.black, size: 30),
            onPressed: () {},
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TextField(
                decoration: InputDecoration(
                  prefixIcon: Icon(Icons.search),
                  hintText: 'Search event',
                  filled: true,
                  fillColor: Colors.grey[200],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(30),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
              SizedBox(height: 20),
              _buildSectionBox('Upcoming', 120),
              SizedBox(height: 20),
              _buildScrollableBox('Today\'s Schedule'),
            ],
          ),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.calendar_today), label: 'Schedules'),
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Maps'),
          BottomNavigationBarItem(icon: Icon(Icons.restaurant), label: 'Dining'),
        ],
        type: BottomNavigationBarType.fixed,
        onTap: (index) {
          // Handle navigation based on the selected index
        },
      ),
    );
  }

  Widget _buildSectionBox(String title, double height) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          Row(
            children: [
              Expanded(child: _buildEmptyBox()),
              SizedBox(width: 10),
              Expanded(child: _buildEmptyBox()),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildEmptyBox() {
    return Container(
      height: 80,
      decoration: BoxDecoration(
        color: Colors.grey,
        borderRadius: BorderRadius.circular(10),
      ),
    );
  }

  Widget _buildScrollableBox(String title) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          SizedBox(
            height: 200, // Scrollable Area Height
            child: Scrollbar(
              thumbVisibility: false,
              child: ListView.builder(
                itemCount: 5,
                itemBuilder: (context, index) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 5.0),
                    child: _buildEmptyBox(),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
