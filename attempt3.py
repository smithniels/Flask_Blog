<!DOCTYPE html>
<html>

<head>
    <title>Niels' Blog</title>
    <!-- <meta name="viewport" content="width=device-width, initial-scale=1"> -->
    <link rel="shortcut icon" type="image/x-icon" href="C:\Users\19258\Desktop\code\Active\attempt\static\nsFavicon4.ico">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>

<body>
  <header class="top">

    <div>
        <span >
            {% if session.logged_in %}
            <a href="/logout/"><span class="glyphicon glyphicon-log-out"></span> Logout </a>
        {% else %}
        <a href="/login/"><span class="glyphicon glyphicon-log-in"></span> Login </a>
        <a href="/register/"><span class="glyphicon glyphicon-pencil"></span> Sign up</a> {% endif %}
        </span>
    </div>
    <div class="title">
      Niels Blog
    </div>
    <span class="right">
      <!-- class = fa is referring to the Font Awesome stylesheet -->
          <a href="https://twitter.com/KneelsS" class="fa fa-twitter"></a>
          <a href="https://www.instagram.com/smithkneels/" class="fa fa-instagram "></a>
          <span > smithniels@gmail.com</span>
     </span>
     </header>



        <div class="container">
            {% for message in get_flashed_messages() %}
            <div class="flash">{{ message }}</div>
            {% endfor %} {% if error %}
            <p class="error"><strong>Error:</strong> {{ error }}</p>
            {% endif %}

            <!-- inheritance -->
            {% block content %} {% endblock %}
            <!-- end inheritance -->

        </div>
    </div>

</body>

</html>
