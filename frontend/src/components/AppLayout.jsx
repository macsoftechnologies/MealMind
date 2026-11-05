import {
  NavLink,
  Outlet,
  useNavigate,
} from "react-router-dom";
import {
  LayoutDashboard,
  HeartPulse,
  Utensils,
  Camera,
  History,
  UserRound,
  Menu,
  LogOut,
} from "lucide-react";

import { useState } from "react";
import { useAuth } from "../context/AuthContext";

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
  logout();
  navigate("/login");
};

  const navigation = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Health Profile",
      path: "/health-profile",
      icon: HeartPulse,
    },
    {
      name: "Diet Plan",
      path: "/diet-plan",
      icon: Utensils,
    },
    {
      name: "Analyze Meal",
      path: "/meal-analysis",
      icon: Camera,
    },
    {
      name: "History",
      path: "/history",
      icon: History,
    },
  ];

  return (
    <div className="app-shell">

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>

        <div className="brand">
          <div className="brand-icon">
            <HeartPulse size={25} />
          </div>

          <div>
            <h2>MealMind</h2>
            <span>Smart Nutrition</span>
          </div>
        </div>

        <nav className="navigation">

          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.name}
                to={item.path}
                end={item.path === "/"}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""}`
                }
              >
                <Icon size={20} />

                <span>{item.name}</span>
              </NavLink>
            );
          })}

        </nav>

        <div className="sidebar-footer">

        <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
          >
        <LogOut size={18} />
        <span>Logout</span>
        </button>

        <p>Your nutrition companion</p>

        </div>

      </aside>

      {/* Main area */}
      <div className="main-wrapper">

        <header className="topbar">

          <button
            className="menu-button"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={24} />
          </button>

          <div className="topbar-title">
            <span>MealMind — Smart Nutrition, Made Personal.</span>
          </div>

          <div className="profile-button">
            <div className="avatar">
              <UserRound size={20} />
            </div>


            <div className="profile-text">
              <strong>{user?.name || "MealMind User"}</strong>
              <span>{user?.email || "My Profile"}</span>
            </div>
          </div>

        </header>

        <main className="main-content">
          <Outlet />
        </main>

      </div>

    </div>
  );
}

export default AppLayout;