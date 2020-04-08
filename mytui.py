import urwid

receipts = ['Number 1', 'Number 2', 'Number 3']

def main():
    body = [urwid.Text(u"Hello World"), urwid.Divider()]
    for r in receipts:
        button = urwid.Button(r)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    main = urwid.ListBox(urwid.SimpleFocusListWalker(body))
    loop = urwid.MainLoop(main)
    loop.run()

if '__main__'==__name__:
    main()
