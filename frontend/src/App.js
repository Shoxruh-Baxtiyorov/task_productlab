import {
    BrowserRouter, Route, Routes
} from "react-router-dom";
import Offers from "./components/Offers";
import Tasks from "./components/Tasks";
import OfferPage from './components/OfferPage';
import TaskPage from "./components/TaskPage";
import Welcome from "./components/Welcome";
import Messenger from "./components/Messenger";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
          <Routes>
              <Route path={'/'} element={<Welcome/>}/>
              <Route path={'offers'} element={<Offers/>}/>
              <Route path={'tasks'} element={<Tasks/>}/>
              <Route path={'offer/:id'} element={<OfferPage/>}/>
              <Route path={'task/:id'} element={<TaskPage/>}/>
              <Route path={'messenger/:id?'} element={<Messenger/>}/>
          </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
