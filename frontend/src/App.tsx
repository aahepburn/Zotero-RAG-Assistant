// src/App.tsx
import React from "react";
import { HashRouter as Router, Routes, Route } from "react-router-dom";
import AppShell from "./components/layout/AppShell";
import Settings from "./pages/Settings";
import "./styles/globals.css";
import "./styles/theme.css";
import { ChatProvider } from "./contexts/ChatContext";
import { SessionsProvider } from "./contexts/SessionsContext";
import { SettingsProvider } from "./contexts/SettingsContext";
import { ProfileProvider } from "./contexts/ProfileContext";

const App: React.FC = () => (
	<Router>
		<ProfileProvider>
			<SettingsProvider>
				<SessionsProvider>
					<ChatProvider>
						<Routes>
							<Route path="/" element={<AppShell />} />
							<Route path="/settings" element={<Settings />} />
						</Routes>
					</ChatProvider>
				</SessionsProvider>
			</SettingsProvider>
		</ProfileProvider>
	</Router>
);

export default App;
