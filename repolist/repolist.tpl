<html>
	<head>
		<title>SoftGroup Interactive Subversion Access</title>
		<style type="text/css">
			body {
				font: 12px Verdana;
			}
		</style>
	</head>

	<body>
		<h1>SoftGroup Interactive Developer Services</h1>

		<p>
			Subversion access is provided to SoftGroup Interactive developers and the
			open source community. Please use it wisely. If you need access to a repository
			email the administrator. This service is monitored by using it you consent to
			that monitoring.
		</p>

		<h2>Public</h2>
		<ul>
			% for repo in unlocked_repos:
			<li><a href="${repo[1]}">${repo[0]}</a></li>
			% endfor
		</ul>
		
		<h2>Password Protected</h2>
		<ul>
			% for repo in locked_repos:
			<li><a href="${repo[1]}">${repo[0]}</a></li>
			% endfor
		</ul>
	</body>
</html>

