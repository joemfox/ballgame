import React, {useEffect,useState} from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useParams } from 'react-router-dom'
import Cookies from "universal-cookie"
import { cn } from "@/lib/utils"

import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"

import { ScrollArea } from "@/components/ui/scroll-area"
import Team from './pages/Team.jsx'
import Players from './pages/Players.jsx'
import PlayerDetail from './pages/PlayerDetail.jsx'
import Standings from './pages/Standings.jsx'
import Draft from './pages/Draft.jsx'
import Settings from './pages/Settings.jsx'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import LineupCard from '@/components/Lineup.jsx'
import ThemeToggle from '@/components/ThemeToggle.jsx'

// Apply saved theme before first render
;(function () {
  const stored = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  if (stored === 'dark' || (!stored && prefersDark)) {
    document.documentElement.classList.add('dark')
  }
})()

function TeamRoute({ team, rosterVersion, onRosterChange }) {
  const { teamid } = useParams()
  return <Team team={team} viewTeam={teamid} rosterVersion={rosterVersion} onRosterChange={onRosterChange} />
}

const cookies = new Cookies();
function App() {
  const [loginState, setLoginState] = useState({
    username: "",
    password: "",
    error: "",
    isAuthenticated: false,
  })
  const [team, setTeam] = useState(null)
  const [isAdmin, setIsAdmin] = useState(false)
  const [isLoggingIn, setIsLoggingIn] = useState(false)
  const [rosterVersion, setRosterVersion] = useState(0)
  const onRosterChange = () => setRosterVersion(v => v + 1)

  useEffect(() => {
    getSession()
  },[])

  function getWhoami() {
    fetch("/api/whoami/", { credentials: "same-origin" })
      .then((res) => res.json())
      .then((data) => { if (data.team) setTeam(data.team); if (data.is_staff) setIsAdmin(true) })
      .catch((err) => { console.log(err) })
  }

  function getSession(){
    fetch("/api/session/", {
      credentials: "same-origin",
    })
    .then((res) => res.json())
    .then((data) => {
      if (data.isAuthenticated) {
        setLoginState({isAuthenticated: true});
        getWhoami();
      } else {
        setLoginState({isAuthenticated: false});
      }
    })
    .catch((err) => {
      console.log(err);
    });
  }

  function isResponseOk(response) {
    if (response.status >= 200 && response.status <= 299) {
      return response.json();
    } else {
      throw Error(response.statusText);
    }
  }

  function login(event){
    event.preventDefault();
    setIsLoggingIn(true)
    fetch(`/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": cookies.get("csrftoken"),
      },
      credentials: "same-origin",
      body: JSON.stringify({username: loginState.username, password: loginState.password}),
    })
    .then(isResponseOk)
    .then((data) => {
      setLoginState({isAuthenticated: true, username: "", password: "", error: ""});
      getWhoami();
    })
    .catch((err) => {
      setLoginState({error: "Wrong username or password."});
    })
    .finally(() => {
      setIsLoggingIn(false)
    });
  }

  const handlePasswordChange = (event) => {
    setLoginState({password: event.target.value});
  }

  const handleUserNameChange = (event) => {
    setLoginState({username: event.target.value});
  }

  function logout(){
    fetch("/api/logout/", {
      credentials: "same-origin",
    })
    .then(isResponseOk)
    .then((data) => {
      console.log(data);
      setLoginState({isAuthenticated: false});
    })
    .catch((err) => {
      console.log(err);
    });
  };
  const defaultLayout = [20, 80]
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [rosterOpen, setRosterOpen] = useState(false)

  // Detect mobile (< 768px), reactive to resize
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < 768)
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 767px)')
    const handler = (e) => setIsMobile(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  if(!loginState.isAuthenticated){
    return (
      <div className="min-h-screen flex items-center justify-center relative">
        <div className="absolute top-4 right-4"><ThemeToggle /></div>
        <div className="w-full max-w-sm p-8 border rounded-lg shadow-sm bg-card text-card-foreground">
          <h1 className="text-2xl font-semibold mb-1">ballgame</h1>
          <p className="text-sm text-muted-foreground mb-6">Sign in to your account</p>
          <form onSubmit={login} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium mb-1">Username</label>
              <Input type="text" id="username" name="username" onChange={handleUserNameChange} />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1">Password</label>
              <Input type="password" id="password" name="password" onChange={handlePasswordChange} />
              {loginState.error && <p className="text-sm text-red-500 mt-1">{loginState.error}</p>}
            </div>
            <button type="submit" disabled={isLoggingIn}
              className="w-full bg-primary text-primary-foreground rounded-md px-4 py-2 text-sm font-medium hover:bg-primary/90 disabled:opacity-50">
              {isLoggingIn ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
        </div>
      </div>
    )
  }
  const routes = (
    <Routes>
      <Route path="/" element={<Team team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange}/>}/>
      <Route path="/players" element={<Players team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange}/>} />
      <Route path="/team/:teamid" element={<TeamRoute team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange}/>} />
      <Route path="/player/:playerid" element={<PlayerDetail />} />
      <Route path="/standings" element={<Standings />} />
      <Route path="/draft" element={<Draft team={team} isAdmin={isAdmin} />} />
      <Route path="/settings" element={<Settings onTeamUpdate={(abbr) => setTeam(abbr)} />} />
    </Routes>
  )

  return (
    <Router>
      <header>
        <div className="flex items-center justify-between py-3 px-4 h-14 w-full">
          <h2 className="text-lg font-semibold"><a href="/">ballgame [alpha]</a></h2>
          <nav className="flex items-center gap-4 text-sm">
            <Link to="/">My Team</Link>
            <Link to="/players">Players</Link>
            <Link to="/standings">Standings</Link>
            <Link to="/draft">Draft</Link>
            <Link to="/settings">Settings</Link>
            <ThemeToggle />
          </nav>
        </div>
        <Separator/>
      </header>
      <DndProvider backend={HTML5Backend}>
        {isMobile ? (
          <main>
            {/* Drawer */}
            <div
              style={{ maxHeight: rosterOpen ? '70vh' : '0', transition: 'max-height 0.3s ease-in-out' }}
              className="overflow-hidden border-b"
            >
              <ScrollArea className="h-[70vh]">
                <LineupCard team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange}/>
              </ScrollArea>
            </div>
            {/* Folder tab */}
            <div className="flex justify-center">
              <button
                onClick={() => setRosterOpen(o => !o)}
                className="px-6 py-0.5 text-xs font-medium text-muted-foreground bg-muted border border-t-0 rounded-b-md leading-5"
              >
                {rosterOpen ? '▲ roster' : '▼ roster'}
              </button>
            </div>
            <div className="px-4 pt-4 overflow-y-auto h-[calc(100vh-56px)]">
              {routes}
            </div>
          </main>
        ) : (
          <main className="pl-4 pr-4 border">
            <ResizablePanelGroup
              direction="horizontal"
              onLayout={(sizes) => {
                cookies.set(`react-resizable-panels:layout`, `${JSON.stringify(sizes)}`)
              }}
              className="h-full max-h-[100vh] items-stretch"
            >
              <ResizablePanel
                defaultSize={defaultLayout[0]}
                minSize={15}
                maxSize={20}
                className={`border-r-2  pt-4 ${cn(isCollapsed && "min-w-[50px] transition-all duration-300 ease-in-out")}`}
              >
                <ScrollArea className="h-[calc(100vh-80px)]">
                  <LineupCard team={team} rosterVersion={rosterVersion} onRosterChange={onRosterChange}/>
                </ScrollArea>
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={defaultLayout[1]} minSize={30}>
                <div className="m-auto  pt-4 w-auto px-4 h-[calc(100vh-80px)] overflow-y-auto">
                  {routes}
                </div>
              </ResizablePanel>
            </ResizablePanelGroup>
          </main>
        )}
      </DndProvider>
      <footer>
        <div className="w-full h-16"></div>
      </footer>
    </Router>
  )
}

export default App


export const ItemTypes = {
    PLAYER: 'Player',
    'C':'C',
    '1B':'1B',
    '2B':'2B',
    '3B':'3B',
    'SS':'SS',
    'LF':'LF',
    'CF':'CF',
    'RF':'RF',
    'SP':'SP',
    'RP':'RP'
  }