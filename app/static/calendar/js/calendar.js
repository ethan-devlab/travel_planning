!function() {

  var today = moment();

  // Color to type mapping
  const colorTypeMap = {
    'orange': '工作',
    'blue': '運動',
    'yellow': '家庭',
    'green': '旅行'
  };

  fetch('/api/events/')
  .then(res => res.json())
  .then(events => {
    window.data = events.map(ev => ({
      id: ev.id,
      eventName: ev.eventName,
      calendar: ev.color,
      color: ev.color,
      type: colorTypeMap[ev.color] || '其他',
      date: moment(ev.date)
    }));

    window.calendar = new Calendar('#calendar', window.data);
  });

  function Calendar(selector, events) {
    this.el = document.querySelector(selector);
    this.events = events;
    this.current = moment().date(1);
    this.draw();
    var current = document.querySelector('.today');
    if(current) {
      var self = this;
      window.setTimeout(function() {
        self.openDay(current);
      }, 500);
    }
  }

  Calendar.prototype.draw = function() {
    this.drawHeader();
    this.drawMonth();
  }

  Calendar.prototype.drawHeader = function() {
    var self = this;
    if(!this.header) {
      this.header = createElement('div', 'header');
      this.header.className = 'header';

      this.title = createElement('h1');

      var right = createElement('div', 'right');
      right.addEventListener('click', function() { self.nextMonth(); });

      var left = createElement('div', 'left');
      left.addEventListener('click', function() { self.prevMonth(); });

      this.header.appendChild(this.title); 
      this.header.appendChild(right);
      this.header.appendChild(left);
      this.el.appendChild(this.header);
    }

    this.title.innerHTML = this.current.format('MMMM YYYY');
  }

  Calendar.prototype.drawMonth = function() {
    var self = this;
    
    this.events.forEach(function(ev) {
      if (!ev.date) return;
      if (typeof ev.date === 'string') {
        ev.date = moment(ev.date);
      }
    });
    
    if(this.month) {
      this.oldMonth = this.month;
      this.oldMonth.className = 'month out ' + (self.next ? 'next' : 'prev');
      this.oldMonth.addEventListener('webkitAnimationEnd', function() {
        self.oldMonth.parentNode.removeChild(self.oldMonth);
        self.month = createElement('div', 'month');
        self.backFill();
        self.currentMonth();
        self.fowardFill();
        self.el.appendChild(self.month);
        window.setTimeout(function() {
          self.month.className = 'month in ' + (self.next ? 'next' : 'prev');
        }, 16);
      });
    } else {
        this.month = createElement('div', 'month');
        this.el.appendChild(this.month);
        this.backFill();
        this.currentMonth();
        this.fowardFill();
        this.month.className = 'month new';
    }
  }

  Calendar.prototype.backFill = function() {
    var clone = this.current.clone();
    var dayOfWeek = clone.day();

    if(!dayOfWeek) { return; }

    clone.subtract('days', dayOfWeek+1);

    for(var i = dayOfWeek; i > 0 ; i--) {
      this.drawDay(clone.add('days', 1));
    }
  }

  Calendar.prototype.fowardFill = function() {
    var clone = this.current.clone().add('months', 1).subtract('days', 1);
    var dayOfWeek = clone.day();

    if(dayOfWeek === 6) { return; }

    for(var i = dayOfWeek; i < 6 ; i++) {
      this.drawDay(clone.add('days', 1));
    }
  }

  Calendar.prototype.currentMonth = function() {
    var clone = this.current.clone();

    while(clone.month() === this.current.month()) {
      this.drawDay(clone);
      clone.add('days', 1);
    }
  }

  Calendar.prototype.getWeek = function(day) {
    if(!this.week || day.day() === 0) {
      this.week = createElement('div', 'week');
      this.month.appendChild(this.week);
    }
  }

  Calendar.prototype.drawDay = function(day) {
    var self = this;
    this.getWeek(day);

    var outer = createElement('div', this.getDayClass(day));
    outer.addEventListener('click', function() {
      self.openDay(this);
    });

    var name = createElement('div', 'day-name', day.format('ddd'));
    var number = createElement('div', 'day-number', day.format('DD'));
    var events = createElement('div', 'day-events');
    
    this.drawEvents(day, events);

    outer.appendChild(name);
    outer.appendChild(number);
    outer.appendChild(events);
    this.week.appendChild(outer);
  }

  Calendar.prototype.drawEvents = function(day, element) {
    if(day.month() === this.current.month()) {
      var todaysEvents = this.events.reduce(function(memo, ev) {
        if(ev.date.isSame(day, 'day')) {
          memo.push(ev);
        }
        return memo;
      }, []);

      todaysEvents.forEach(function(ev) {
        var evSpan = createElement('span', 'event-indicator ' + ev.color);
        evSpan.innerText = ev.type || '活動'; 
        evSpan.title = ev.eventName; 
        element.appendChild(evSpan);
      });
    }
  }

  Calendar.prototype.getDayClass = function(day) {
    classes = ['day'];
    if(day.month() !== this.current.month()) {
      classes.push('other');
    } else if (today.isSame(day, 'day')) {
      classes.push('today');
    }
    return classes.join(' ');
  }

  Calendar.prototype.openDay = function(el) {
    var details, arrow;
    var dayNumber = +el.querySelectorAll('.day-number')[0].innerText || +el.querySelectorAll('.day-number')[0].textContent;
    var day = this.current.clone().date(dayNumber);

    var currentOpened = document.querySelector('.details');

    if(currentOpened && currentOpened.parentNode === el.parentNode) {
      details = currentOpened;
      arrow = document.querySelector('.arrow');
    } else {
      if(currentOpened) {
        currentOpened.addEventListener('webkitAnimationEnd', function() {
          currentOpened.parentNode.removeChild(currentOpened);
        });
        currentOpened.addEventListener('oanimationend', function() {
          currentOpened.parentNode.removeChild(currentOpened);
        });
        currentOpened.addEventListener('msAnimationEnd', function() {
          currentOpened.parentNode.removeChild(currentOpened);
        });
        currentOpened.addEventListener('animationend', function() {
          currentOpened.parentNode.removeChild(currentOpened);
        });
        currentOpened.className = 'details out';
      }

      details = createElement('div', 'details in');
      var arrow = createElement('div', 'arrow');

      details.appendChild(arrow);
      el.parentNode.appendChild(details);
    }

    var todaysEvents = this.events.reduce(function(memo, ev) {
      if(ev.date.isSame(day, 'day')) {
        memo.push(ev);
      }
      return memo;
    }, []);

    const oldEvents = details.querySelector('.events');
    if (oldEvents) details.removeChild(oldEvents);

    this.renderEvents(todaysEvents, details);

    arrow.style.left = el.offsetLeft - el.parentNode.offsetLeft + 27 + 'px';
  }

  // Enhanced renderEvents with delete functionality and event type display
  Calendar.prototype.renderEvents = function(events, ele) {
    var self = this;
    var currentWrapper = ele.querySelector('.events');
    var wrapper = createElement('div', 'events in' + (currentWrapper ? ' new' : ''));

    events.forEach(function(ev) {
      var eventDiv = createElement('div', 'event');
      
      var eventContent = createElement('div', 'event-content');
      var square = createElement('div', 'event-category ' + ev.color);
      var span = createElement('span', 'event-name', ev.eventName);
      var typeSpan = createElement('span', 'event-type ' + ev.color, ev.type || '其他');
      
      eventContent.appendChild(square);
      eventContent.appendChild(span);
      eventContent.appendChild(typeSpan);
      
      // Add delete button
      var deleteBtn = createElement('button', 'delete-btn');
      deleteBtn.innerHTML = '<i class="ri-delete-bin-line"></i>';
      deleteBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        self.deleteEvent(ev.id, eventDiv);
      });

      eventDiv.appendChild(eventContent);
      eventDiv.appendChild(deleteBtn);
      wrapper.appendChild(eventDiv);
    });

    if(!events.length) {
      var div = createElement('div', 'event empty');
      var span = createElement('span', '', '此日無活動');
      div.appendChild(span);
      wrapper.appendChild(div);
    }

    if(currentWrapper) {
      currentWrapper.className = 'events out';
      currentWrapper.addEventListener('webkitAnimationEnd', function() {
        currentWrapper.parentNode.removeChild(currentWrapper);
        ele.appendChild(wrapper);
      });
      currentWrapper.addEventListener('oanimationend', function() {
        currentWrapper.parentNode.removeChild(currentWrapper);
        ele.appendChild(wrapper);
      });
      currentWrapper.addEventListener('msAnimationEnd', function() {
        currentWrapper.parentNode.removeChild(currentWrapper);
        ele.appendChild(wrapper);
      });
      currentWrapper.addEventListener('animationend', function() {
        currentWrapper.parentNode.removeChild(currentWrapper);
        ele.appendChild(wrapper);
      });
    } else {
      ele.appendChild(wrapper);
    }
  }

  // Delete event
  Calendar.prototype.deleteEvent = function(eventId, eventElement) {
    if (!confirm('確定要刪除此活動嗎？')) {
      return;
    }

    var self = this;

    fetch('/api/delete_event/' + eventId + '/', {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': getCSRFToken()
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        // Remove from global data
        window.data = window.data.filter(ev => ev.id !== eventId);
        
        // Update the calendar's events array
        self.events = window.data;

        // Remove the event element with animation
        eventElement.style.opacity = '0';
        eventElement.style.transform = 'translateX(-100%)';
        
        setTimeout(function() {
          if (eventElement.parentNode) {
            eventElement.parentNode.removeChild(eventElement);
            
            // Check if this was the last event in the day
            var eventsContainer = eventElement.closest('.events');
            if (eventsContainer && eventsContainer.children.length === 0) {
              // Add empty message
              var div = createElement('div', 'event empty');
              var span = createElement('span', '', '此日無活動');
              div.appendChild(span);
              eventsContainer.appendChild(div);
            }
          }
          
          // Redraw calendar to update event dots
          self.draw();
        }, 300);

      } else {
        alert('刪除失敗，請重試');
      }
    })
    .catch(err => {
      console.error('Delete error:', err);
      alert('刪除失敗，請重試');
    });
  }

  Calendar.prototype.nextMonth = function() {
    this.current.add('months', 1);
    this.next = true;
    this.draw();
  }

  Calendar.prototype.prevMonth = function() {
    this.current.subtract('months', 1);
    this.next = false;
    this.draw();
  }

  window.Calendar = Calendar;

  function createElement(tagName, className, innerText) {
    var ele = document.createElement(tagName);
    if(className) {
      ele.className = className;
    }
    if(innerText) {
      ele.innerText = ele.textContent = innerText;
    }
    return ele;
  }
}();

!function() {
  window.addEvent = function () {
    const name = document.getElementById('event-name').value;
    const dateStr = document.getElementById('event-date').value;
    const color = document.getElementById('event-color').value;
    
    if (!name || !dateStr || !color) {
      alert("請填寫所有欄位");
      return;
    }

    fetch('/api/add_event/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify({
        eventName: name,
        date: dateStr,
        color: color
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        const date = moment(dateStr);
        const colorTypeMap = {
          'orange': '工作',
          'blue': '運動',
          'yellow': '家庭',
          'green': '旅行'
        };
        
        const newEvent = {
          id: data.id,
          eventName: name,
          calendar: color,
          color: color,
          type: colorTypeMap[color] || '其他',
          date: date
        };
        
        // Add to global data
        window.data.push(newEvent);
        
        // Update calendar's events array
        window.calendar.events = window.data;
        
        // Redraw calendar
        window.calendar.draw();

        // Clear form
        document.getElementById('event-name').value = '';
        document.getElementById('event-date').value = '';
        document.getElementById('event-color').value = 'orange';

        // Open the day with the new event
        const allDayEls = document.querySelectorAll('.day');
        for (let el of allDayEls) {
          const numberEl = el.querySelector('.day-number');
          if (!numberEl) continue;

          const dayNum = numberEl.textContent;
          const dayDate = window.calendar.current.clone().date(dayNum);

          if (dayDate.isSame(date, 'day')) {
            window.calendar.openDay(el);
            break;
          }
        }
      } else {
        alert('新增活動失敗');
      }
    })
    .catch(err => {
      console.error('Add event error:', err);
      alert('新增活動失敗，請重試');
    });
  };

  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('add-event-button');
    if (btn) {
      btn.addEventListener('click', window.addEvent);
    }

    // Add enter key support for form
    const form = document.querySelector('.event-form');
    if (form) {
      form.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          window.addEvent();
        }
      });
    }
  });
}();

function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return '';
}