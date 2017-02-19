drop table if exists stories;
create table stories (
  id integer primary key autoincrement,
  title text not null,
  story_text text not null,
  criteria text not null,
  value int not null,
  estimation int not null,
  status text not null
);
