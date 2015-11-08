
import requests
import json

class Organization:
    def __init__(self, url, user, passwd):
        self.url = url
        self.user = user
        self.passwd = passwd
        self.projects = []

        # try to connect and log in?

    def get_projects(self):
        # skip if already read
        if len(self.projects) == 0:
            r = requests.get(self.url +  '/api/projects', auth = (self.user, self.passwd))
            #r = requests.get('http://samples-dev.testspace.com/api/projects', auth = ('timd', self.passwd))
            print(r.headers['content-type'])
            print(r.json())
            # r.json() is list of dict
            for p in r.json():
                prj = Project(self, **p)
                self.projects.append(prj)
        return self.projects

    def find_project(self, name):
        self.get_projects()
        for p in self.projects:
            if p.name == name:
                return p
        return None

    def copy_project_and_spaces(self, src_proj):
        #print(json.dumps(src_proj.__dict__))
        # create project
        r = requests.post(self.url +  '/api/projects', auth = (self.user, self.passwd), data = (src_proj.get_json()))
        # todo: validate return
        print(r)
        if r.headers['Status'] != '201 Created':
            raise ValueError('Attempting to create Project "' + src_proj.name + '"' + r.text)

        dest_proj = Project(self, **r.json())

        # now copy each space
        src_org = src_proj.parent_org
        #GET /api/projects/:project_id/spaces
        r = requests.get(src_org.url + '/api/projects/' + str(src_proj.id) + '/spaces', auth = (src_org.user, src_org.passwd))
        print(r.json())
        for s in r.json():
            # create space in dest
            # POST /api/projects/:project_id/spaces
            s['project'] = src_proj.name
            resp = requests.post(dest_org.url + '/api/projects/' + str(dest_proj.id) + '/spaces' , data = (json.dumps(s)), auth = (dest_org.user, dest_org.passwd))
            print(resp)

class Project(object):
    def __init__(self, parent_org, **entries):
        self.parent_org = parent_org
        # convert dictionary entries to members
        self.__dict__.update(entries)
    def get_json(self):
        # work with a copy
        d = self.__dict__.copy()
        # remove non-pod members
        for key ,value in d.items():
            if isinstance(value, Organization):
                d.pop(key)
        return json.dumps(d)

class Space(object):
    def __init__(self, parent_proj, **entries):
        #self.parent_org = parent_org
        # convert dictionary entries to members
        self.__dict__.update(entries)
        # remove parent_org from dict



##########
src_org = Organization('http://samples-dev.testspace.com', 'timd', 'seaside')
src_proj = src_org.find_project('temp')

dest_org = Organization('http://barkingpumpkin.stridespace.com', 'timd', 'seaside')
dest_org.copy_project_and_spaces(src_proj)

