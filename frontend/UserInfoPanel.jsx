import React, { useContext } from 'react';
import { ChatContext } from '../context/ChatContext';
// allow the user to put in information like their kaggle leaderboard username and the competition name and let's themm update as well
function UserInfoPanel() {
  const {
    username,
    competitionName,
    setUsername,
    setCompetitionName,
  } = useContext(ChatContext);

  return (
    <div style={{ padding: '20px', background: '#fff', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h2>User Information</h2>
      <label>
        Kaggle Username:
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ marginLeft: '10px', padding: '5px', width: '200px' }}
        />
      </label>
      <br />
      <label style={{ marginTop: '10px' }}>
        Competition Name:
        <input
          type="text"
          value={competitionName}
          onChange={(e) => setCompetitionName(e.target.value)}
          style={{ marginLeft: '10px', padding: '5px', width: '200px' }}
        />
      </label>
    </div>
  );
}