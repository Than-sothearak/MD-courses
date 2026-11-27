# MD Courses

Open this folder in VS Code, right-click the root `index.html`, and choose **Open with Live Server**. You can also click **Go Live** and visit:

http://localhost:5500/

Choose a course folder, then click a lesson. Use your browser's Back button to return to the lesson list, or **All courses** on a course page to return home. Live Server refreshes the browser when you save a file.

After adding, renaming, or removing lesson HTML files or course folders, rebuild the navigation:

```sh
python3 build_navigation.py
```

This also prepares exported lessons for Live Server: it escapes body-closing tags inside JavaScript strings so the reload script is inserted into the page correctly. This preserves the lesson content and the strings' runtime values.

If Live Server is unavailable, run `python3 -m http.server 5500` from this folder and open the same URL. This fallback serves the files without automatic refresh. Stop it with Ctrl+C.

The navigation and lessons are static files and can also be served by a static web host. The localhost URL is only for this computer; it is not a public website.
# MD-courses
