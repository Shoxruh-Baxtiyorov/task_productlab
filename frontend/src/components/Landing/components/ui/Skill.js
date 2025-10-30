import React from 'react';

const Skill = ({ label }) => {
  return (
    <span className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700 ring-1 ring-inset ring-slate-200">
      {label}
    </span>
  );
};

export default Skill;
