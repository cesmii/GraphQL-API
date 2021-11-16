import React from "react";
import { Switch, Route, Redirect } from "react-router-dom";

// components

import Sidebar from "components/Sidebar/Sidebar.js";
import HeaderStats from "components/Headers/HeaderStats.js";

// views

import Dashboard from "views/admin/Dashboard.js";

export default function Admin() {
  return (
    <>
      <Sidebar />
      <div className="relative md:ml-64 bg-blueGray-100">
        {/* Header */}
        
        <div className="px-4 md:px-10 mx-auto w-full -m-24">
          <Switch>
            <Route path="/admin/dashboard" exact component={Dashboard} />
            <Redirect from="/admin" to="/admin/dashboard" />
          </Switch>
        </div>
      </div>
    </>
  );
}
