import {combineReducers} from "@reduxjs/toolkit";
import offers from "./offers";
import tasks from "./tasks";
import users from "./users";
import messages from "./messages";
export default combineReducers({
    offers,
    tasks,
    users,
    messages
});